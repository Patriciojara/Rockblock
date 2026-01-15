import queue
import time

# Creamos una cola vacía
q = queue.Queue()

print("🔹 Creamos una cola vacía")
print("Tamaño inicial:", q.qsize())
print()

# Simulamos que el sensor produce datos
for i in range(3):
    dato = f"posicion_{i}"
    print(f"📤 Sensor genera -> {dato}")
    q.put(dato)  # Encolamos el dato
    print(f"  ➕ Cola ahora tiene {q.qsize()} elementos\n")
    time.sleep(0.5)

# Simulamos que el logger empieza a leer
print("🔸 Logger empieza a leer datos...\n")

while not q.empty():
    valor = q.get()   # Saca el primer dato en la cola (FIFO)
    print(f"📥 Logger saca -> {valor}")
    print(f"  ➖ Cola ahora tiene {q.qsize()} elementos\n")
    time.sleep(0.8)

print("✅ Cola vacía, flujo completo terminado")

