#!/bin/bash
# ============================================
# BILBOT - Test Script para Webhook de n8n
# ============================================
# Uso: ./tests/test-webhook.sh [URL_WEBHOOK]
# Ejemplo: ./tests/test-webhook.sh https://your-n8n.app.n8n.cloud/webhook/bilbot

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNED=0
TOTAL_LATENCY=0
LATENCY_COUNT=0

# Test names for summary
declare -a TEST_RESULTS

print_color() {
    echo -e "${1}${2}${NC}"
}

record_pass() {
    PASSED=$((PASSED + 1))
    TEST_RESULTS+=("✅ $1")
}

record_fail() {
    FAILED=$((FAILED + 1))
    TEST_RESULTS+=("❌ $1")
}

record_warn() {
    WARNED=$((WARNED + 1))
    TEST_RESULTS+=("⚠️  $1")
}

record_latency() {
    TOTAL_LATENCY=$((TOTAL_LATENCY + $1))
    LATENCY_COUNT=$((LATENCY_COUNT + 1))
}

# Verificar que se pasó la URL del webhook
if [ -z "$1" ]; then
    print_color "$RED" "❌ Error: Falta la URL del webhook"
    echo "Uso: $0 <URL_WEBHOOK>"
    echo "Ejemplo: $0 https://your-n8n.app.n8n.cloud/webhook/bilbot"
    exit 1
fi

WEBHOOK_URL="$1"

print_color "$BLUE" "🚀 BILBOT Webhook Test Suite"
print_color "$BLUE" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_color "$YELLOW" "📍 Testing webhook: $WEBHOOK_URL"
echo ""

# Test 1: Verificar que el webhook responde
print_color "$BLUE" "Test 1: Verificar disponibilidad del webhook"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$WEBHOOK_URL")

if [ "$response" == "200" ] || [ "$response" == "201" ] || [ "$response" == "302" ]; then
    print_color "$GREEN" "✅ Webhook está activo (HTTP $response)"
    record_pass "Webhook activo"
else
    print_color "$RED" "❌ Webhook no responde correctamente (HTTP $response)"
    record_fail "Webhook activo"
    print_color "$RED" "Abortando tests - webhook no disponible."
    exit 1
fi

echo ""

# Test 2: Enviar mensaje simple
print_color "$BLUE" "Test 2: Mensaje simple - Saludo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Enviando: 'Hola'"

start_time=$(date +%s%3N)

response=$(curl -s -X POST "$WEBHOOK_URL" \
  --max-time 30 \
  -H "Content-Type: application/json" \
  -d '{
    "chatInput": "Hola",
    "sessionId": "test-session-1"
  }')

end_time=$(date +%s%3N)
latency=$((end_time - start_time))
record_latency "$latency"

if echo "$response" | grep -qi "Aitor\|Aupa\|Kaixo\|bilba"; then
    print_color "$GREEN" "✅ Respuesta recibida con personalidad de Aitor"
    print_color "$YELLOW" "⏱️  Latencia: ${latency}ms"
    echo "Extracto: $(echo "$response" | head -c 200)..."
    record_pass "Personalidad de Aitor"
else
    print_color "$RED" "❌ Respuesta no contiene personalidad esperada"
    echo "Respuesta: $response"
    record_fail "Personalidad de Aitor"
fi

echo ""

# Test 3: Búsqueda de lugar
print_color "$BLUE" "Test 3: Búsqueda de lugar - Pintxos"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Enviando: 'Recomiéndame un bar de pintxos en el Casco Viejo'"

start_time=$(date +%s%3N)

response=$(curl -s -X POST "$WEBHOOK_URL" \
  --max-time 30 \
  -H "Content-Type: application/json" \
  -d '{
    "chatInput": "Recomiéndame un bar de pintxos en el Casco Viejo",
    "sessionId": "test-session-2"
  }')

end_time=$(date +%s%3N)
latency=$((end_time - start_time))
record_latency "$latency"

if echo "$response" | grep -iq "Gure Toki\|pintxo\|Casco"; then
    print_color "$GREEN" "✅ Respuesta contiene recomendación de lugar"
    print_color "$YELLOW" "⏱️  Latencia: ${latency}ms"
    echo "Extracto: $(echo "$response" | head -c 300)..."
    record_pass "Búsqueda de lugares"
else
    print_color "$RED" "❌ Respuesta no contiene recomendación esperada"
    echo "Respuesta: $response"
    record_fail "Búsqueda de lugares"
fi

echo ""

# Test 4: Pregunta histórica
print_color "$BLUE" "Test 4: Pregunta histórica - Guggenheim"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Enviando: 'Cuéntame sobre el Guggenheim'"

start_time=$(date +%s%3N)

response=$(curl -s -X POST "$WEBHOOK_URL" \
  --max-time 30 \
  -H "Content-Type: application/json" \
  -d '{
    "chatInput": "Cuéntame sobre el Guggenheim",
    "sessionId": "test-session-3"
  }')

end_time=$(date +%s%3N)
latency=$((end_time - start_time))
record_latency "$latency"

if echo "$response" | grep -iq "Guggenheim\|1997\|Frank Gehry"; then
    print_color "$GREEN" "✅ Respuesta contiene información histórica"
    print_color "$YELLOW" "⏱️  Latencia: ${latency}ms"
    echo "Extracto: $(echo "$response" | head -c 300)..."
    record_pass "Información histórica"
else
    print_color "$RED" "❌ Respuesta no contiene información esperada"
    echo "Respuesta: $response"
    record_fail "Información histórica"
fi

echo ""

# Test 5: Solicitud de itinerario
print_color "$BLUE" "Test 5: Solicitud de itinerario"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Enviando: 'Tengo 2 días en Bilbao, ¿qué hago?'"

start_time=$(date +%s%3N)

response=$(curl -s -X POST "$WEBHOOK_URL" \
  --max-time 30 \
  -H "Content-Type: application/json" \
  -d '{
    "chatInput": "Tengo 2 días en Bilbao, ¿qué hago?",
    "sessionId": "test-session-4"
  }')

end_time=$(date +%s%3N)
latency=$((end_time - start_time))
record_latency "$latency"

if echo "$response" | grep -iq "día\|Guggenheim\|Casco\|itinerario"; then
    print_color "$GREEN" "✅ Respuesta contiene itinerario sugerido"
    print_color "$YELLOW" "⏱️  Latencia: ${latency}ms"
    echo "Extracto: $(echo "$response" | head -c 300)..."
    record_pass "Generación de itinerarios"
else
    print_color "$RED" "❌ Respuesta no contiene itinerario"
    echo "Respuesta: $response"
    record_fail "Generación de itinerarios"
fi

echo ""

# Test 6: Mensaje en inglés (multilingüe)
print_color "$BLUE" "Test 6: Mensaje en inglés - Multilingüe"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Enviando: 'Hello, what are the best museums?'"

start_time=$(date +%s%3N)

response=$(curl -s -X POST "$WEBHOOK_URL" \
  --max-time 30 \
  -H "Content-Type: application/json" \
  -d '{
    "chatInput": "Hello, what are the best museums?",
    "sessionId": "test-session-5"
  }')

end_time=$(date +%s%3N)
latency=$((end_time - start_time))
record_latency "$latency"

if echo "$response" | grep -iq "museum\|Guggenheim\|Fine Arts\|Bellas Artes"; then
    print_color "$GREEN" "✅ Respuesta en inglés correcta"
    print_color "$YELLOW" "⏱️  Latencia: ${latency}ms"
    echo "Extracto: $(echo "$response" | head -c 300)..."
    record_pass "Soporte multilingüe (inglés)"
else
    print_color "$RED" "❌ Respuesta no está en inglés o no contiene información esperada"
    echo "Respuesta: $response"
    record_fail "Soporte multilingüe (inglés)"
fi

echo ""

# Test 7: Expresiones vascas
print_color "$BLUE" "Test 7: Verificar expresiones vascas en respuestas"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

response=$(curl -s -X POST "$WEBHOOK_URL" \
  --max-time 30 \
  -H "Content-Type: application/json" \
  -d '{
    "chatInput": "¿Dónde puedo tomar un café?",
    "sessionId": "test-session-6"
  }')

if echo "$response" | grep -E "(Aupa|Toma ya|macho|Ojo|Agur|Kaixo)" > /dev/null; then
    print_color "$GREEN" "✅ Respuesta incluye expresiones vascas auténticas"
    echo "Expresiones detectadas:"
    echo "$response" | grep -oE "(Aupa|Toma ya|macho|Ojo|Agur|Kaixo)" | sort -u
    record_pass "Expresiones vascas"
else
    print_color "$YELLOW" "⚠️  No se detectaron expresiones vascas típicas"
    record_warn "Expresiones vascas (no detectadas)"
fi

echo ""

# ============================================
# RESUMEN DINÁMICO
# ============================================
TOTAL=$((PASSED + FAILED + WARNED))
AVG_LATENCY=0
if [ "$LATENCY_COUNT" -gt 0 ]; then
    AVG_LATENCY=$((TOTAL_LATENCY / LATENCY_COUNT))
fi

echo ""
print_color "$BLUE" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_color "$BLUE" "📊 RESUMEN DE TESTS"
print_color "$BLUE" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for result in "${TEST_RESULTS[@]}"; do
    echo "  $result"
done

echo ""
print_color "$YELLOW" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Total:    $TOTAL tests"
print_color "$GREEN" "  Passed:   $PASSED"
if [ "$FAILED" -gt 0 ]; then
    print_color "$RED" "  Failed:   $FAILED"
else
    echo "  Failed:   $FAILED"
fi
if [ "$WARNED" -gt 0 ]; then
    print_color "$YELLOW" "  Warnings: $WARNED"
else
    echo "  Warnings: $WARNED"
fi
echo ""
print_color "$YELLOW" "  ⏱️  Latencia promedio: ${AVG_LATENCY}ms"

LATENCY_STATUS="✅ OK"
if [ "$AVG_LATENCY" -gt 3000 ]; then
    LATENCY_STATUS="❌ Excede objetivo (>3s)"
fi
echo "  Objetivo <3000ms: $LATENCY_STATUS"
echo ""

if [ "$FAILED" -eq 0 ]; then
    print_color "$GREEN" "🎉 BILBOT está funcionando correctamente!"
else
    print_color "$RED" "⚠️  BILBOT tiene $FAILED test(s) fallidos. Revisar logs de n8n."
fi
echo ""

exit "$FAILED"
