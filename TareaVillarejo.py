# Homework 2 : Luis Carlos Villarejo    cc 94542302

import time
import random
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

"""def procedimiento_bloqueante():
    inicio = time.perf_counter()
    time.sleep(1)
    print("Proceso ejecutado  ")
    espera_extra = random.uniform(0, 0.5)
    time.sleep(espera_extra)
    fin = time.perf_counter()
    return fin - inicio

def experimento_secuencial():
    inicio_total = time.perf_counter()
    tiempos = []
    for i in range(20):
        t = procedimiento_bloqueante()
        tiempos.append(t)
    return time.perf_counter() - inicio_total

def ejecutar_procedimiento(_):
    return procedimiento_bloqueante()

def experimento_threadpool():
    inicio_total = time.perf_counter()
    with ThreadPoolExecutor(max_workers=10) as executor:
        resultados = list(executor.map(ejecutar_procedimiento, range(20)))
    fin_total = time.perf_counter()
    print(f"Tiempo total de ejecución con hilos: {fin_total - inicio_total:.2f} segundos")
    return fin_total - inicio_total

def ejecutar_procedimiento_proceso(_):
    return procedimiento_bloqueante()

def experimento_processpool():
    inicio_total = time.perf_counter()
    with ProcessPoolExecutor(max_workers=10) as executor:
        resultados = list(executor.map(ejecutar_procedimiento_proceso, range(20)))
    fin_total = time.perf_counter()
    print(f"Tiempo total de ejecución con procesos: {fin_total - inicio_total:.2f} segundos")
    return fin_total - inicio_total"""

def factorial(n:int) -> int:
    resultado = 1
    for i in range(1, n + 1):
        resultado *= i
    return resultado

def suma_factorial_secuencial(n:int) -> int:
    total = 0
    for i in range(1, n + 1):
        total += factorial(i)
    return total

def suma_factoriales_threadpool(inicio:int, fin:int) -> int:
    total = 0
    for i in range(inicio, fin + 1):
        total += factorial(i)
    return total

def experimento_threadpool_factoriales(n:int) -> int:
    rangos = [(1, 1250), (1251, 2500), (2501, 3750), (3751, 5000)]
    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as executor:
        resultados = list(executor.map(lambda r: suma_factoriales_threadpool(r[0], r[1]), rangos))
    fin = time.perf_counter()
    print(f"Tiempo total de ejecución con ThreadPoolExecutor: {fin - inicio:.2f} segundos")
    return sum(resultados)

def ejecutar_rango_proceso(rango):
    incio, fin = rango
    return suma_factoriales_threadpool(incio, fin)

def experimento_processpool_factoriales(n: int) -> int:
    rangos = [(1, 1250), (1251, 2500), (2501, 3750), (3751, 5000)]
    inicio = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as executor:
        resultados = list(executor.map(ejecutar_rango_proceso, rangos))
    fin = time.perf_counter()
    print(f"Tiempo total de ejecución con ProcessPoolExecutor: {fin - inicio:.2f} segundos")
    return sum(resultados)

if __name__ == "__main__":

    """print("Ejecutando experimento secuencial...")
    tiempo_secuencial = experimento_secuencial()
    print(f"Tiempo total de ejecución secuencial: {tiempo_secuencial:.2f} segundos\n")
    print("Ejecutando experimento con ThreadPoolExecutor...")
    tiempo_threadpool = experimento_threadpool()
    print("\nEjecutando experimento con ProcessPoolExecutor...")
    tiempo_processpool = experimento_processpool()"""

    N = 5000
    inicio = time.perf_counter()
    resultado = suma_factorial_secuencial(N)
    fin = time.perf_counter()
    print(f"Tiempo secuencial (1 a {N}): {fin - inicio:.2f} segundos")

    experimento_threadpool_factoriales(N)

    experimento_processpool_factoriales(N)
    


    
