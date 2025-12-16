#!/bin/bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m uvicorn services.transcription_service.api:app --host 0.0.0.0 --port 8000
