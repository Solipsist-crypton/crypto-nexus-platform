Write-Host "рџљЂ Р“Р•РќР•Р РђР¦Р†РЇ Р Р•РђР›Р¬РќРРҐ AI РЎРР“РќРђР›Р†Р’" -ForegroundColor Green
Write-Host "=========================================="

$symbols = @("BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT")

foreach ($symbol in $symbols) {
    Write-Host "`nрџ”Ќ Р“РµРЅРµСЂСѓСЋ СЃРёРіРЅР°Р» РґР»СЏ $symbol..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/futures/signals/generate?symbol=$symbol"
        
        if ($response.status -eq "success") {
            $signal = $response.signal
            Write-Host "   вњ… $($signal.direction.ToUpper()) ($([math]::Round($signal.confidence*100))%)" -ForegroundColor Green
            Write-Host "   рџ’° Р’С…С–Рґ: $$($signal.entry_price)" -ForegroundColor Yellow
            Write-Host "   рџЋЇ TP: $$($signal.take_profit)" -ForegroundColor Green
            Write-Host "   рџ›‘ SL: $$($signal.stop_loss)" -ForegroundColor Red
        } else {
            Write-Host "   вќЊ РџРѕРјРёР»РєР°: $($response | ConvertTo-Json)" -ForegroundColor Red
        }
    } catch {
        Write-Host "   вќЊ РџРѕРјРёР»РєР° Р·Р°РїРёС‚Сѓ: $_" -ForegroundColor Red
    }
}

Write-Host "`nрџ“Љ РџРµСЂРµРІС–СЂРєР° РІСЃС–С… СЃРёРіРЅР°Р»С–РІ..." -ForegroundColor Cyan
try {
    $allSignals = Invoke-RestMethod -Method GET -Uri "http://localhost:5000/api/futures/signals"
    Write-Host "   рџ“€ Р’СЃСЊРѕРіРѕ СЃРёРіРЅР°Р»С–РІ Сѓ Р‘Р”: $($allSignals.count)" -ForegroundColor Green
    
    if ($allSignals.signals.Count -gt 0) {
        foreach ($signal in $allSignals.signals | Select-Object -First 3) {
            Write-Host "      $($signal.symbol) $($signal.direction) ($([math]::Round($signal.confidence*100))%)" -ForegroundColor White
        }
    }
} catch {
    Write-Host "   вќЊ РџРѕРјРёР»РєР°: $_" -ForegroundColor Red
}
