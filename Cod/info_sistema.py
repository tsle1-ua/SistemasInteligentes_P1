#!/usr/bin/env python3
"""
Script para obtener información completa del sistema donde se ejecuta Python
debe instalarse psutil
pip install psutil

"""

import platform
import os
import sys
import socket
from datetime import datetime
import io
import contextlib

def obtener_info_basica():
    """Obtiene información básica del sistema usando módulos incorporados"""
    print("=" * 50)
    print("INFORMACIÓN BÁSICA DEL SISTEMA")
    print("=" * 50)
    
    print(f"Sistema operativo: {platform.system()}")
    print(f"Versión del SO: {platform.version()}")
    print(f"Release: {platform.release()}")
    print(f"Arquitectura: {platform.architecture()[0]}")
    print(f"Procesador: {platform.processor()}")
    print(f"Nombre del equipo: {platform.node()}")
    print(f"Plataforma completa: {platform.platform()}")
    
    try:
        print(f"Usuario actual: {os.getlogin()}")
    except:
        print(f"Usuario actual: {os.environ.get('USER', 'Desconocido')}")
    
    print(f"Directorio home: {os.path.expanduser('~')}")
    print(f"Directorio actual: {os.getcwd()}")

def obtener_info_python():
    """Obtiene información sobre Python"""
    print("\n" + "=" * 50)
    print("INFORMACIÓN DE PYTHON")
    print("=" * 50)
    
    print(f"Versión de Python: {platform.python_version()}")
    print(f"Implementación: {platform.python_implementation()}")
    print(f"Compilador: {platform.python_compiler()}")
    print(f"Executable: {sys.executable}")
    print(f"Ruta de módulos: {sys.path[0]}")

def obtener_info_red():
    """Obtiene información de red básica"""
    print("\n" + "=" * 50)
    print("INFORMACIÓN DE RED")
    print("=" * 50)
    
    try:
        hostname = socket.gethostname()
        ip_local = socket.gethostbyname(hostname)
        print(f"Nombre del host: {hostname}")
        print(f"IP local: {ip_local}")
    except:
        print("No se pudo obtener información de red")

def obtener_info_cpu_detallada():
    """Obtiene información detallada de CPU y procesador"""
    print("\n" + "=" * 50)
    print("INFORMACIÓN DETALLADA DE CPU Y PROCESADOR")
    print("=" * 50)
    
    # Información básica con platform
    print(f"Procesador: {platform.processor()}")
    print(f"Máquina: {platform.machine()}")
    
    # Información específica de macOS usando sysctl
    if platform.system() == 'Darwin':
        try:
            import subprocess
            
            # Nombre del procesador
            try:
                result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Nombre completo del CPU: {result.stdout.strip()}")
            except:
                pass
            
            # Familia del procesador
            try:
                result = subprocess.run(['sysctl', '-n', 'machdep.cpu.family'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Familia del CPU: {result.stdout.strip()}")
            except:
                pass
            
            # Modelo del procesador
            try:
                result = subprocess.run(['sysctl', '-n', 'machdep.cpu.model'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Modelo del CPU: {result.stdout.strip()}")
            except:
                pass
            
            # Características del procesador
            try:
                result = subprocess.run(['sysctl', '-n', 'machdep.cpu.features'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    features = result.stdout.strip()
                    print(f"Características del CPU: {features}")
            except:
                pass
            
            # Caché del procesador
            try:
                cache_info = {}
                for cache_level in ['l1i', 'l1d', 'l2', 'l3']:
                    result = subprocess.run(['sysctl', '-n', f'hw.{cache_level}cachesize'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip() != '0':
                        cache_size = int(result.stdout.strip())
                        if cache_size > 0:
                            cache_info[cache_level] = cache_size
                
                if cache_info:
                    print("Información de caché:")
                    for cache, size in cache_info.items():
                        if size >= 1024*1024:
                            print(f"  {cache.upper()}: {size // (1024*1024)} MB")
                        elif size >= 1024:
                            print(f"  {cache.upper()}: {size // 1024} KB")
                        else:
                            print(f"  {cache.upper()}: {size} bytes")
            except:
                pass
                
        except ImportError:
            pass
    
    try:
        import psutil
        
        # Información de núcleos
        cpu_fisicas = psutil.cpu_count(logical=False)
        cpu_logicas = psutil.cpu_count(logical=True)
        print(f"Núcleos físicos: {cpu_fisicas}")
        print(f"Núcleos lógicos (threads): {cpu_logicas}")
        
        if cpu_fisicas and cpu_logicas:
            print(f"Hyperthreading: {'Sí' if cpu_logicas > cpu_fisicas else 'No'}")
            if cpu_logicas > cpu_fisicas:
                print(f"Threads por núcleo: {cpu_logicas // cpu_fisicas}")
        
        # Información de frecuencias
        try:
            freq = psutil.cpu_freq()
            if freq:
                print(f"Frecuencia actual: {freq.current:.2f} MHz")
                print(f"Frecuencia mínima: {freq.min:.2f} MHz")
                print(f"Frecuencia máxima: {freq.max:.2f} MHz")
            
            # Frecuencias por núcleo (si está disponible)
            try:
                freq_per_cpu = psutil.cpu_freq(percpu=True)
                if freq_per_cpu and len(freq_per_cpu) > 1:
                    print(f"Frecuencias por núcleo:")
                    for i, freq_cpu in enumerate(freq_per_cpu[:8]):  # Mostrar solo los primeros 8
                        print(f"  CPU {i}: {freq_cpu.current:.2f} MHz")
                    if len(freq_per_cpu) > 8:
                        print(f"  ... y {len(freq_per_cpu) - 8} núcleos más")
            except:
                pass
        except:
            print("Información de frecuencia: No disponible")
        
        # Uso de CPU
        print(f"\nUso actual de CPU: {psutil.cpu_percent(interval=1)}%")
        
        # Uso por núcleo
        try:
            cpu_percent_per_core = psutil.cpu_percent(percpu=True, interval=1)
            print(f"Uso por núcleo:")
            for i, percent in enumerate(cpu_percent_per_core[:8]):  # Mostrar solo los primeros 8
                print(f"  CPU {i}: {percent}%")
            if len(cpu_percent_per_core) > 8:
                print(f"  ... y {len(cpu_percent_per_core) - 8} núcleos más")
        except:
            print("Uso por núcleo: No disponible")
        
        # Estadísticas de CPU
        try:
            cpu_stats = psutil.cpu_stats()
            print(f"\nEstadísticas de CPU:")
            print(f"  Cambios de contexto: {cpu_stats.ctx_switches:,}")
            print(f"  Interrupciones: {cpu_stats.interrupts:,}")
            print(f"  Llamadas al sistema: {cpu_stats.syscalls:,}")
            if hasattr(cpu_stats, 'soft_interrupts'):
                print(f"  Interrupciones suaves: {cpu_stats.soft_interrupts:,}")
        except:
            print("Estadísticas de CPU: No disponibles")
        
        # Tiempos de CPU
        try:
            cpu_times = psutil.cpu_times()
            total_time = sum(cpu_times)
            print(f"\nTiempos de CPU (porcentajes):")
            print(f"  Usuario: {(cpu_times.user / total_time * 100):.1f}%")
            print(f"  Sistema: {(cpu_times.system / total_time * 100):.1f}%")
            print(f"  Inactivo: {(cpu_times.idle / total_time * 100):.1f}%")
            if hasattr(cpu_times, 'nice'):
                print(f"  Nice: {(cpu_times.nice / total_time * 100):.1f}%")
            if hasattr(cpu_times, 'iowait'):
                print(f"  I/O Wait: {(cpu_times.iowait / total_time * 100):.1f}%")
        except:
            print("Tiempos de CPU: No disponibles")
            
    except ImportError:
        print("Para información detallada de CPU, instala psutil: pip install psutil")

def obtener_info_avanzada():
    """Obtiene información avanzada si psutil está disponible"""
    try:
        import psutil
        
        print("\n" + "=" * 50)
        print("INFORMACIÓN AVANZADA DEL HARDWARE")
        print("=" * 50)
        
        # Memoria
        memoria = psutil.virtual_memory()
        print(f"Memoria total: {memoria.total / (1024**3):.2f} GB")
        print(f"Memoria disponible: {memoria.available / (1024**3):.2f} GB")
        print(f"Memoria usada: {memoria.percent}%")
        
        # Disco
        disco = psutil.disk_usage('/')
        print(f"Disco total: {disco.total / (1024**3):.2f} GB")
        print(f"Disco libre: {disco.free / (1024**3):.2f} GB")
        print(f"Disco usado: {(disco.used / disco.total) * 100:.1f}%")
        
        # Tiempo de arranque
        boot_time = psutil.boot_time()
        boot_datetime = datetime.fromtimestamp(boot_time)
        print(f"Tiempo de arranque: {boot_datetime}")
        
        # Procesos
        print(f"Número de procesos activos: {len(psutil.pids())}")
        
    except ImportError:
        print("\n" + "=" * 50)
        print("INFORMACIÓN AVANZADA NO DISPONIBLE")
        print("=" * 50)
        print("Para obtener información avanzada del hardware, instala psutil:")
        print("pip install psutil")

def main():
    """Función principal"""
    archivo_salida = "informacion_sistema.txt"
    
    # Mostrar información completa en consola
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Información del sistema - " + timestamp)
    
    obtener_info_basica()
    obtener_info_python()
    obtener_info_red()
    obtener_info_cpu_detallada()
    obtener_info_avanzada()
    
    print("\n" + "=" * 50)
    print("ANÁLISIS COMPLETADO")
    print("=" * 50)
    
    # Generar archivo solo con las secciones específicas
    try:
        # Capturar solo las secciones específicas
        output_buffer = io.StringIO()
        original_stdout = sys.stdout
        
        try:
            sys.stdout = output_buffer
            
            # Solo ejecutar las funciones específicas para el archivo
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("Información del sistema - " + timestamp)
            print()
            
            obtener_info_cpu_detallada()
            obtener_info_avanzada()
            
            print("\n" + "=" * 50)
            print("ANÁLISIS COMPLETADO")
            print("=" * 50)
            
        finally:
            sys.stdout = original_stdout
        
        # Guardar el contenido filtrado en archivo
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(output_buffer.getvalue())
        
        print(f"\n✅ Información del sistema guardada en: {archivo_salida}")
        print(f"📄 Archivo creado: {os.path.abspath(archivo_salida)}")
        print(f"📋 Contenido: Solo CPU y Hardware avanzado")
        
        output_buffer.close()
        
    except Exception as e:
        print(f"❌ Error al guardar el archivo: {e}")

if __name__ == "__main__":
    main()