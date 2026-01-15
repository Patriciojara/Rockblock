import threading
import queue
import time
import random


# ---- Parámetros de demo ----
PRODUCE_HZ = 10          # sensor: ~10 lecturas por segundo
CONSUME_HZ = 5           # logger: ~5 escrituras por segundo (a propósito, más lento)
QUEUE_MAX = 50           # tamaño máximo de la cola (backpressure)
RUN_SECONDS = 6          # tiempo de ejecución de la demo

# ---- Recursos compartidos ----
q = queue.Queue(maxsize=QUEUE_MAX)
stop_event = threading.Event() # Detiene los hilos

def sensor_thread():
    """Hilo productor: simula lecturas de posición."""
    periodo = 1.0 / PRODUCE_HZ
    while not stop_event.is_set():
        dato = {
            "t": time.time(),                # marca de tiempo "de pared" (humana)
            "pos": random.uniform(0, 100),   # simulamos posición
        }
        try:
            # put con timeout: si la cola está llena, espera un poco y si no, tira queue.Full
            q.put(dato, timeout=0.2)
            # print(f"[SENSOR] → encolado t={dato['t']:.2f}, pos={dato['pos']:.2f}")
        except queue.Full:
            # backpressure: si el consumidor no da abasto, puedes contar drops o bloquear
            print("⚠️  Cola llena: descartando medición (o podrías bloquear aquí)")
        time.sleep(periodo)
    print("Sensor: stop limpio")

def logger_thread():
    """Hilo consumidor: simula escritura lenta (p.ej., SQLite)."""
    periodo = 1.0 / CONSUME_HZ
    procesados = 0
    while not stop_event.is_set() or not q.empty():
        try:
            item = q.get(timeout=0.5)   # espera hasta 0.5 s por un dato
        except queue.Empty:
            continue  # sigue intentando hasta que llegue algo o se ordene parar
        # Aquí iría la escritura real (p.ej., INSERT a SQLite)
        procesados += 1
        print(f"[LOGGER] t={item['t']:.2f}, pos={item['pos']:.2f} | cola={q.qsize()}")
        time.sleep(periodo)
    print(f"Logger: stop limpio. Total procesados={procesados}")

def main():
    t_s = threading.Thread(target=sensor_thread, name="Sensor")
    t_l = threading.Thread(target=logger_thread, name="Logger")

    t_s.start()
    t_l.start()

    try:
        time.sleep(RUN_SECONDS)   # corre la demo unos segundos
    except KeyboardInterrupt:
        print("\n⛔ Interrumpido por usuario")
    finally:
        # Señal de parada y espera de cierre ordenado
        stop_event.set()
        t_s.join()
        t_l.join()
        print("✅ Todos los hilos terminaron correctamente")

if __name__ == "__main__":
    main()
