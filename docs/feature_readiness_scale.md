# Feature Readiness Scale

| Level | Label               | Beschreibung |
| ----- | ------------------- | ------------ |
| 0     | Not Available       | Feature oder kritische Abhängigkeit fehlt; kein Pilotbetrieb möglich. |
| 1     | Limited             | Basissystem erreichbar, aber Smoke-Tests oder Kernfunktionen schlagen fehl. |
| 2     | Ready (Warnings)    | Funktion verfügbar, Smoke-Tests ok, aber bekannte Issues/Warnungen vorhanden. |
| 3     | Pilot Ready         | Alle Checks bestanden, keine offenen Blocker – geeignet für Pilot-Release. |

Der Readiness-Score ergibt sich aus Availability-Status, Smoke-Test-Ergebnissen und der Anzahl dokumentierter Issues pro Feature.
