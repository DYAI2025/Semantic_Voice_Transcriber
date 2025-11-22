# 📁 Ordner-Anleitung für WhatsApp Audio-Dateien

**Last Updated:** 2025-11-19 | **Verified against commit:** 75fdfbbc

## 🎯 Wo soll ich meine OPUS-Dateien ablegen?

Die OPUS-Dateien (WhatsApp Audio) gehören in den **`Eingang/`** Ordner, organisiert nach Chatpartnern:

```
whisper_speaker_matcher/
└── Eingang/
    ├──  name#1/                      ← Audio-Dateien von/ name#
    ├──  name#2/       ← Audio-Dateien von/zu  name#
    ├──  name#3/                   ← Audio-Dateien von/ name#
    ├── name#4/                   ← Audio-Dateien von/ name#
    ├── name#5/                  ← Audio-Dateien von/ name#
    └── name#6/   ← Audio-Dateien von/zu  name#
```

## 📱 WhatsApp Audio-Dateien Beispiele

Typische WhatsApp Audio-Dateinamen:
- `WhatsApp Audio 2025-06-29 at 13.20.58.opus`
- `WhatsApp Audio 2025-01-12 at 15.30.45.opus`

## 🔄 Verarbeitungsreihenfolge

1. **Zuerst:** Alle Dateien im `Zoe/` Ordner (Priorität!)
2. **Dann:** Alle anderen Ordner alphabetisch
3. **Innerhalb jedes Ordners:** Neueste Aufnahmen zuerst

## 📝 Was passiert bei der Verarbeitung?

### Input:
```
Eingang/name#/WhatsApp Audio 2025-06-29 at 13.20.58.opus
```

### Output:
```
Transkripte_LLM/2025-06-29_13-20-58_ name#_WhatsApp Audio 2025-06-29 at 13.20.58_transkript.md
```

### Inhalt des Transkripts:
```markdown
# WhatsApp Audio Transkription

**Chat mit:**  name#1
**Aufnahme am:** 29.06.2025 um 13:20:58
**Verarbeitet am:** 03.07.2025 um 12:30:15
**Original-Datei:** WhatsApp Audio 2025-06-29 at 13.20.58.opus

## Zeitstempel:
- **Aufnahme-Datum:** 2025-06-29
- **Aufnahme-Uhrzeit:** 13:20:58
- **Verarbeitungszeit:** 2025-07-03 12:30:15

## Transkription:

**[ name#1 - 13:20:58]:** Hey, ich wollte dir nur sagen, dass...

## Kontext für LLM:
Diese Nachricht wurde am 29.06.2025 um 13:20:58 in einem WhatsApp-Chat zwischen mir und  name#1 aufgenommen.
```

## 🚀 So startest du die Verarbeitung:

```bash
cd /Users/yourname/foldertoyoure/whisper_speaker_matcher

# V3 System mit Datum/Zeit-Extraktion (Empfohlen!)
python3 auto_transcriber_v3.py --local
```

## 💡 Tipps:

1. **Ordne deine Dateien vor der Verarbeitung** - Das System erkennt den Chatpartner automatisch aus dem Ordnernamen
2. **Zoe's Nachrichten zuerst** - Werden automatisch priorisiert
3. **Dateinamen bleiben original** - Das System extrahiert Datum/Zeit automatisch
4. **MP4 werden ignoriert** - Nur OPUS-Dateien werden verarbeitet

## 🎯 Ergebnis:

- **LLM-optimierte Markdown-Dateien** mit allen Zeitstempeln
- **Chatpartner im Dateinamen** für einfache Zuordnung
- **Original-Aufnahmezeit** sowohl im Dateinamen als auch im Transkript
- **Perfekt für weitere AI-Verarbeitung** formatiert

## 📊 Nach der Verarbeitung:

Schaue in den `Transkripte_LLM/` Ordner:
- Alle fertigen Transkripte
- `verarbeitungs_report.md` mit Statistiken
- Dateinamen zeigen sofort Datum, Zeit und Chatpartner

**Viel Erfolg mit der Transkription! 🎉**  
