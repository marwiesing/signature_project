# Signature Project – KI-gestützte Webanwendung im Home-Lab

[![Mirror on GitHub](https://img.shields.io/badge/Mirror-GitHub-blue?logo=github)](https://github.com/marwiesing/signature_project)

---

## Projektbeschreibung

Das Signature Project ist eine vollständig lokal betriebene Webanwendung, die moderne DevOps-Prinzipien, containerisierte Bereitstellung und KI-Integration vereint.  
Die Anwendung basiert auf Flask, verwendet eine PostgreSQL-Datenbank für die Datenhaltung und bindet lokale Large Language Models (LLMs) über eine REST-API an.

Das Projekt wurde entwickelt, um eine sichere, unabhängige Plattform für interaktive Chats mit lokal betriebenen KI-Modellen zu schaffen – vollständig offline-fähig und ohne externe Abhängigkeiten.

---

## Hauptfunktionen

- **Mehrbenutzersystem** Registrierung und Login 
- **Projekt- und Chatverwaltung** mit übersichtlicher Sidebar
- **Interaktive Chatoberfläche** mit Markdown-Rendering und Scrollmanagement
- **Integration lokaler LLMs** (DeepSeek Coder / R1) über Ollama-API
- **Exportfunktion**: Chats als Markdown-Datei herunterladen
- **Persistente Speicherung** aller Daten in einer strukturierten PostgreSQL-Datenbank
- **Containerisierung** mit automatisierten Build- und Deployment-Prozessen (Docker, GitLab CI/CD, ArgoCD)

---

## Technische Komponenten

| Komponente            | Beschreibung |
| ---------------------- | ------------- |
| **Backend**             | Flask (Python 3.12) |
| **Frontend**            | HTML-Templates (Bootstrap 5) |
| **Datenbank**           | PostgreSQL |
| **LLM-Integration**     | Ollama + lokale Modelle (DeepSeek Coder / DeepSeek R1) |
| **Deployment**          | Docker, GitLab CI/CD, ArgoCD (GitOps) |


---

## Installation und Betrieb

> **Hinweis:** Dieses Projekt ist für eine Kubernetes-Umgebung mit lokalem GitLab, ArgoCD und Registry ausgelegt.

1. **Voraussetzungen:**
   - Kubernetes-Cluster (z. B. mit kubeadm eingerichtet)
   - Lokale Docker Registry
   - GitLab Runner für CI/CD
   - Ollama Server mit DeepSeek-Modellen

2. **Schritte:**
   - Quellcode clonen:  
     ```bash
     git clone https://github.com/marwiesing/signature_project.git
     ```
   - Umgebungsvariablen in `.env`-Datei anpassen (z. B. Datenbankzugang, Ollama-Host)
   - Docker-Image lokal bauen oder CI/CD verwenden
   - Deployment über ArgoCD synchronisieren (manifests/)

Weitere Details zur Installation finden sich direkt im Projekt-Repository.

---

## Projektstatus

✅ Stabile Version V1.0.0 veröffentlicht  
✅ Volle Funktionalität implementiert  
🔜 Geplante Erweiterungen: zusätzliche Modellunterstützung, erweiterte Nutzerrollen

✅ **Fehlerbehebungen & Verbesserungen in V1.1.0**

* Datenbankschema: txshortname ergänzt und Kurznamen (R1/Coder) hinterlegt
* Chat-Header: Anzeige von Projekt- und Chat-Namen (Projekt > Chat)
* Bot-Antworten: Kurzname in jeder Nachricht und konsistente XML-/Markdown-Ausgabe
* Timeout-Handling: Unterbrechung der Reload-Schleife, Inline-Fehlermeldung
* Projektliste/UI: Layout-Update, Felder für Name/Beschreibung/Created korrigiert
* Chat-Formular: Inline-Fehlermeldung, scrollbare & widths-lock für .chat-box
* Templates & Routen: Datenübergabe und Paare-Logik optimiert


---

## Verweise

- Ollama: [https://ollama.com](https://ollama.com)
- DeepSeek Coder: [https://ollama.com/library/deepseek-coder](https://ollama.com/library/deepseek-coder)
- DeepSeek R1: [https://ollama.com/library/deepseek-r1](https://ollama.com/library/deepseek-r1)

---

## Autor

Entwickelt und dokumentiert von [Martin Wiesinger](https://github.com/marwiesing).

---

