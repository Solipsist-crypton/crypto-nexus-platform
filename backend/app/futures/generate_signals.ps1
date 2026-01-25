# Створи файл generate_signals.ps1
@'
Write-Host "🚀 ГЕНЕРАЦІЯ РЕАЛЬНИХ AI СИГНАЛІВ" -ForegroundColor Green
Write-Host "=========================================="

$symbols = @("BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT")

foreach ($symbol in $symbols) {
    Write-Host "`n🔍 Генерую сигнал для $symbol..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/futures/signals/generate?symbol=$symbol"
        
        if ($response.status -eq "success") {
            $signal = $response.signal
            Write-Host "   ✅ $($signal.direction.ToUpper()) ($([math]::Round($signal.confidence*100))%)" -ForegroundColor Green
            Write-Host "   💰 Вхід: $$($signal.entry_price)" -ForegroundColor Yellow
            Write-Host "   🎯 TP: $$($signal.take_profit)" -ForegroundColor Green
            Write-Host "   🛑 SL: $$($signal.stop_loss)" -ForegroundColor Red
        } else {
            Write-Host "   ❌ Помилка: $($response | ConvertTo-Json)" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ❌ Помилка запиту: $_" -ForegroundColor Red
    }
}

Write-Host "`n📊 Перевірка всіх сигналів..." -ForegroundColor Cyan
try {
    $allSignals = Invoke-RestMethod -Method GET -Uri "http://localhost:5000/api/futures/signals"
    Write-Host "   📈 Всього сигналів у БД: $($allSignals.count)" -ForegroundColor Green
    
    if ($allSignals.signals.Count -gt 0) {
        foreach ($signal in $allSignals.signals | Select-Object -First 3) {
            Write-Host "      $($signal.symbol) $($signal.direction) ($([math]::Round($signal.confidence*100))%)" -ForegroundColor White
        }
    }
} catch {
    Write-Host "   ❌ Помилка: $_" -ForegroundColor Red
}
'@ | Out-File -FilePath "generate_signals.ps1" -Encoding UTF8

# Запусти скрипт
.\generate_signals.ps1