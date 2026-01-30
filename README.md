# 🌿 IA GreenByteAde

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Prototipo-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 🧠 Descripción del Proyecto

[Describe aquí el objetivo del modelo de IA. Ejemplo: Sistema de visión por computadora para detectar plásticos en ríos, o un modelo predictivo para optimizar el consumo energético en servidores.]

**Objetivos Principales:**
* [Objetivo 1: Ej. Clasificar imágenes con un 90% de precisión.]
* [Objetivo 2: Ej. Reducir el tiempo de procesamiento de datos.]

## 📂 Estructura del Dataset

La información utilizada para entrenar el modelo proviene de [Fuente de los datos: Ej. Kaggle / Sensores propios].

| Variable | Tipo de Dato | Descripción |
| :--- | :---: | :--- |
| `input_img` | Matriz (Tensor) | Imágenes RGB de 256x256 px |
| `label` | Entero (0-4) | Clase del residuo (0=Papel, 1=Plástico...) |
| `timestamp` | Datetime | Fecha y hora de la recolección |

> **Nota:** Si el dataset es muy pesado, no lo subas a GitHub. Incluye un script `download_data.sh` o un enlace a Google Drive/S3.

## 🛠️ Instalación y Requisitos

Se recomienda utilizar un entorno virtual (Virtualenv o Conda) para evitar conflictos.

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/ArdannyR/iagreenbyteade.git](https://github.com/ArdannyR/iagreenbyteade.git)
    cd iagreenbyteade
    ```

2.  **Crear entorno virtual (Opcional pero recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Uso / Ejecución

Hay dos formas de ejecutar este proyecto:

### 1. Entrenamiento del Modelo
Para re-entrenar el modelo con nuevos datos:
```bash
python src/train.py --epochs 50 --batch_size 32
