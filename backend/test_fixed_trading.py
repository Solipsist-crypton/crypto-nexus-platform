# test_orchestrator.py
import sys
sys.path.append('.')
from app.futures.services.signal_orchestrator import SignalOrchestrator

orchestrator = SignalOrchestrator()
signal = orchestrator.generate_signal('BTC/USDT:USDT')
print(signal)