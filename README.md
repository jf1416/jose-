# CRM Local

Aplicación web simple para gestionar clientes de un negocio de préstamos.

## Requisitos

- Python 3
- Dependencias listadas en `requirements.txt`

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

## Uso

Inicia la base de datos y ejecuta la aplicación:

```bash
python app.py
```

La aplicación estará disponible en `http://127.0.0.1:5000/`.

### Funcionalidades

- Registrar clientes con número de préstamo, nombre, cédula, dirección, localidad y nota.
- Listar, editar y eliminar clientes.
- Consultar por número de préstamo, cédula o nombre.
- Agregar comentarios de seguimiento.
- Exportar el listado de clientes a Excel.
