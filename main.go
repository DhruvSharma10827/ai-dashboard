package main

import (
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

var (
	titleStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#7c3aed")).
			Bold(true).
			Padding(1, 2)

	boxStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("#4a4a6a")).
			Padding(1, 2)

	menuStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#888888"))
)

type model struct {
	selected int
}

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			return m, tea.Quit
		case "up", "k":
			if m.selected > 0 {
				m.selected--
			}
		case "down", "j":
			if m.selected < 5 {
				m.selected++
			}
		case "enter":
			// Handle selection
		}
	}
	return m, nil
}

func (m model) View() string {
	s := titleStyle.Render("🤖 AI Dashboard v1.0 - Enterprise Edition")
	s += "\n\n"
	
	menu := []string{
		"[1] Dashboard",
		"[2] AI Models",
		"[3] Agents",
		"[4] Chat",
		"[5] Tasks",
		"[6] Settings",
	}
	
	for i, item := range menu {
		if i == m.selected {
			s += "  ▶ " + item + "\n"
		} else {
			s += "    " + item + "\n"
		}
	}
	
	s += "\n" + boxStyle.Render("Status: Ready | Models: 5 | Agents: 4 | Tasks: 0")
	s += "\n\n" + menuStyle.Render("↑/↓ Navigate | Enter Select | q Quit")
	
	return s
}

func main() {
	p := tea.NewProgram(initialModel())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
}

func initialModel() model {
	return model{selected: 0}
}
