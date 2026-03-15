package types

import "time"

// User represents a dashboard user
type User struct {
	ID           int       `json:"id" db:"id"`
	Username     string    `json:"username" db:"username"`
	PasswordHash string    `json:"-" db:"password_hash"`
	Salt         string    `json:"-" db:"salt"`
	Role         string    `json:"role" db:"role"`
	CreatedAt    time.Time `json:"created_at" db:"created_at"`
	LastLogin    time.Time `json:"last_login" db:"last_login"`
}

// AIModel represents an AI model configuration
type AIModel struct {
	ID           int       `json:"id" db:"id"`
	Name         string    `json:"name" db:"name"`
	Provider     string    `json:"provider" db:"provider"`
	ModelID      string    `json:"model_id" db:"model_id"`
	Endpoint     string    `json:"endpoint" db:"endpoint"`
	APIKey       string    `json:"-" db:"api_key"`
	MaxTokens    int       `json:"max_tokens" db:"max_tokens"`
	Temperature  float64   `json:"temperature" db:"temperature"`
	Status       string    `json:"status" db:"status"`
	CreatedAt    time.Time `json:"created_at" db:"created_at"`
	LastUsed     time.Time `json:"last_used" db:"last_used"`
}

// Agent represents an AI agent
type Agent struct {
	ID          int       `json:"id" db:"id"`
	Name        string    `json:"name" db:"name"`
	Description string    `json:"description" db:"description"`
	ModelID     int       `json:"model_id" db:"model_id"`
	SystemPrompt string   `json:"system_prompt" db:"system_prompt"`
	Status      string    `json:"status" db:"status"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
}

// Task represents a task in the system
type Task struct {
	ID          int       `json:"id" db:"id"`
	Title       string    `json:"title" db:"title"`
	Description string    `json:"description" db:"description"`
	Status      string    `json:"status" db:"status"`
	Priority    string    `json:"priority" db:"priority"`
	AgentID     *int      `json:"agent_id" db:"agent_id"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	CompletedAt *time.Time `json:"completed_at" db:"completed_at"`
}

// ChatMessage represents a chat message
type ChatMessage struct {
	ID        int       `json:"id" db:"id"`
	SessionID string    `json:"session_id" db:"session_id"`
	Role      string    `json:"role" db:"role"`
	Content   string    `json:"content" db:"content"`
	ModelID   int       `json:"model_id" db:"model_id"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}

// ChatSession represents a chat session
type ChatSession struct {
	ID        string    `json:"id" db:"id"`
	Name      string    `json:"name" db:"name"`
	ModelID   int       `json:"model_id" db:"model_id"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

// SystemStatus represents system status information
type SystemStatus struct {
	CPUUsage     float64   `json:"cpu_usage"`
	MemoryUsage  float64   `json:"memory_usage"`
	DiskUsage    float64   `json:"disk_usage"`
	Uptime       string    `json:"uptime"`
	ActiveModels int       `json:"active_models"`
	ActiveAgents int       `json:"active_agents"`
	PendingTasks int       `json:"pending_tasks"`
}

// ProviderType defines AI provider types
type ProviderType string

const (
	ProviderOllama ProviderType = "ollama"
	ProviderOpenAI ProviderType = "openai"
	ProviderClaude ProviderType = "claude"
)

// Screen represents different TUI screens
type Screen int

const (
	ScreenLogin Screen = iota
	ScreenDashboard
	ScreenModels
	ScreenAgents
	ScreenChat
	ScreenTasks
	ScreenSettings
)

// Config represents application configuration
type Config struct {
	Server   ServerConfig   `mapstructure:"server"`
	Database DatabaseConfig `mapstructure:"database"`
	Security SecurityConfig `mapstructure:"security"`
	AI       AIConfig       `mapstructure:"ai"`
	Logging  LoggingConfig  `mapstructure:"logging"`
}

type ServerConfig struct {
	Port    int  `mapstructure:"port"`
	SSHPort int  `mapstructure:"ssh_port"`
	SSH     bool `mapstructure:"ssh"`
}

type DatabaseConfig struct {
	Path string `mapstructure:"path"`
}

type SecurityConfig struct {
	SessionTimeout  int `mapstructure:"session_timeout"`
	MaxLoginAttempts int `mapstructure:"max_login_attempts"`
}

type AIConfig struct {
	DefaultProvider string `mapstructure:"default_provider"`
	DefaultModel    string `mapstructure:"default_model"`
}

type LoggingConfig struct {
	Level  string `mapstructure:"level"`
	Format string `mapstructure:"format"`
	Output string `mapstructure:"output"`
}
