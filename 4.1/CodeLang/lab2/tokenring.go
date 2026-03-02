package main

import (
	"flag"
	"fmt"
	"math/rand"
	"sync"
	"time"

	// В Go 1.25 sha3 находится в golang.org/x/crypto/sha3
	// Но для простоты примера используем sha256 из стандартной библиотеки
	"crypto/sha256"
)

// Token представляет сообщение, передаваемое по кольцу
type Token struct {
	Data       []byte // Произвольные данные сообщения
	TargetHash []byte // SHA256 хэш идентификатора получателя
	TTL        int    // Время жизни сообщения (количество пересылок)
}

// Node представляет узел в TokenRing
type Node struct {
	ID       int          // Идентификатор узла
	Hash     []byte       // SHA256 хэш идентификатора (для быстрого сравнения)
	Incoming <-chan Token // Канал для получения сообщений от предыдущего узла
	Outgoing chan<- Token // Канал для отправки сообщений следующему узлу
}

// NodeManager управляет всеми узлами и их соединениями
type NodeManager struct {
	nodes    []*Node
	channels []chan Token
	wg       sync.WaitGroup
	stopChan chan struct{}
}

// NewNodeManager создает и связывает узлы в кольцо
func NewNodeManager(nodeCount int) *NodeManager {
	if nodeCount < 2 {
		panic("TokenRing требует минимум 2 узла")
	}

	manager := &NodeManager{
		nodes:    make([]*Node, nodeCount),
		channels: make([]chan Token, nodeCount),
		stopChan: make(chan struct{}),
	}

	// Создаем каналы для каждого узла
	for i := 0; i < nodeCount; i++ {
		manager.channels[i] = make(chan Token, 10) // Буферизированный канал
	}

	// Создаем узлы и связываем их в кольцо
	for i := 0; i < nodeCount; i++ {
		// Вычисляем SHA256 хэш от идентификатора
		hash := sha256.Sum256([]byte(fmt.Sprintf("%d", i)))

		// Каждый узел получает данные из канала i-1 и отправляет в канал i
		// Для первого узла (i=0) предыдущим является последний узел (i-1 с учетом модуля)
		prevIdx := (i - 1 + nodeCount) % nodeCount

		manager.nodes[i] = &Node{
			ID:       i,
			Hash:     hash[:],
			Incoming: manager.channels[prevIdx], // Получаем из канала предыдущего узла
			Outgoing: manager.channels[i],       // Отправляем в свой канал для следующего узла
		}
	}

	return manager
}

// Start запускает все узлы
func (m *NodeManager) Start() {
	for _, node := range m.nodes {
		m.wg.Add(1)
		go m.runNode(node)
	}
}

// Stop останавливает все узлы
func (m *NodeManager) Stop() {
	close(m.stopChan)

	// Закрываем все каналы, чтобы узлы завершили работу
	for _, ch := range m.channels {
		close(ch)
	}

	// Ждем завершения всех горутин
	m.wg.Wait()
}

// runNode основной цикл обработки сообщений для узла
func (m *NodeManager) runNode(node *Node) {
	defer m.wg.Done()

	// Генератор случайных чисел для этого узла
	rng := rand.New(rand.NewSource(time.Now().UnixNano() + int64(node.ID)))

	for {
		select {
		case <-m.stopChan:
			fmt.Printf("[УЗЕЛ %d] Получен сигнал остановки\n", node.ID)
			return

		case token, ok := <-node.Incoming:
			if !ok {
				// Канал закрыт
				return
			}

			// Логируем получение сообщения
			fmt.Printf("[УЗЕЛ %d] Получен токен: данные='%s', TTL=%d, целевой хэш=%x\n",
				node.ID, string(token.Data), token.TTL, token.TargetHash)

			// Проверяем, является ли этот узел получателем
			if m.isTarget(node, token.TargetHash) {
				fmt.Printf("[УЗЕЛ %d] СООБЩЕНИЕ ДОСТАВЛЕНО: данные='%s'\n",
					node.ID, string(token.Data))

				// Генерируем новое случайное сообщение
				m.sendRandomMessage(node, rng)
				continue
			}

			// Проверяем время жизни
			if token.TTL <= 0 {
				fmt.Printf("[УЗЕЛ %d] СООБЩЕНИЕ УТРАЧЕНО (TTL истек): данные='%s'\n",
					node.ID, string(token.Data))

				// Генерируем новое случайное сообщение
				m.sendRandomMessage(node, rng)
				continue
			}

			// Уменьшаем TTL и передаем дальше
			token.TTL--
			fmt.Printf("[УЗЕЛ %d] Пересылаю токен -> узлу %d, новый TTL=%d\n",
				node.ID, (node.ID+1)%len(m.nodes), token.TTL)

			// Отправляем следующему узлу
			select {
			case node.Outgoing <- token:
			case <-m.stopChan:
				return
			}
		}
	}
}

// isTarget проверяет, является ли узел целевым получателем
func (m *NodeManager) isTarget(node *Node, targetHash []byte) bool {
	if len(node.Hash) != len(targetHash) {
		return false
	}
	for i := range node.Hash {
		if node.Hash[i] != targetHash[i] {
			return false
		}
	}
	return true
}

// sendRandomMessage генерирует и отправляет случайное сообщение
func (m *NodeManager) sendRandomMessage(node *Node, rng *rand.Rand) {
	// Проверяем, не остановлена ли система
	select {
	case <-m.stopChan:
		return
	default:
	}

	// Генерируем случайного получателя (исключая текущий узел)
	targetID := rng.Intn(len(m.nodes))
	for targetID == node.ID && len(m.nodes) > 1 {
		targetID = rng.Intn(len(m.nodes))
	}

	// Вычисляем хэш целевого узла
	targetHash := sha256.Sum256([]byte(fmt.Sprintf("%d", targetID)))

	// Генерируем случайные данные
	dataLength := rng.Intn(20) + 5 // Длина от 5 до 25 символов
	data := make([]byte, dataLength)
	for i := range data {
		data[i] = byte(rng.Intn(26) + 65) // Случайные буквы A-Z
	}

	// TTL от 5 до 15
	ttl := rng.Intn(11) + 5

	token := Token{
		Data:       data,
		TargetHash: targetHash[:],
		TTL:        ttl,
	}

	fmt.Printf("[УЗЕЛ %d] ГЕНЕРИРУЮ новое сообщение для узла %d: данные='%s', TTL=%d\n",
		node.ID, targetID, string(data), ttl)

	// Отправляем следующему узлу
	select {
	case node.Outgoing <- token:
	case <-m.stopChan:
		return
	}
}

// SendInitialMessage отправляет первое сообщение от основного потока узлу 1
func (m *NodeManager) SendInitialMessage() {
	// Выбираем случайного получателя (не узел 1)
	rng := rand.New(rand.NewSource(time.Now().UnixNano()))
	targetID := rng.Intn(len(m.nodes))
	for targetID == 1 && len(m.nodes) > 1 {
		targetID = rng.Intn(len(m.nodes))
	}

	// Вычисляем хэш целевого узла
	targetHash := sha256.Sum256([]byte(fmt.Sprintf("%d", targetID)))

	// Создаем сообщение
	token := Token{
		Data:       []byte("Первое сообщение"),
		TargetHash: targetHash[:],
		TTL:        10,
	}

	fmt.Printf("[MAIN] Отправляю первое сообщение узлу 1 для доставки узлу %d\n", targetID)

	// Отправляем узлу 1 (через его входящий канал)
	// Узел 1 получает из канала последнего узла (nodeCount-1)
	lastNodeIdx := len(m.nodes) - 1

	select {
	case m.channels[lastNodeIdx] <- token:
	case <-m.stopChan:
		return
	}
}

func main() {
	// Парсим аргументы командной строки
	nodeCount := flag.Int("nodes", 5, "количество узлов в TokenRing")
	duration := flag.Int("time", 10, "время работы в секундах")
	flag.Parse()

	if *nodeCount < 2 {
		fmt.Println("Ошибка: требуется минимум 2 узла")
		return
	}

	fmt.Printf("Запуск TokenRing с %d узлами на %d секунд\n", *nodeCount, *duration)
	fmt.Println("Используется SHA256 для хэширования (из стандартной библиотеки)")

	// Создаем и запускаем менеджер узлов
	manager := NewNodeManager(*nodeCount)
	manager.Start()

	// Отправляем первое сообщение
	manager.SendInitialMessage()

	// Ждем указанное время
	fmt.Printf("\nРабота в течение %d секунд...\n", *duration)
	time.Sleep(time.Duration(*duration) * time.Second)

	// Останавливаем все узлы
	fmt.Println("\nЗавершение работы TokenRing...")
	manager.Stop()
	fmt.Println("Программа завершена")
}
