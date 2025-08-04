# 🚀 Cómo crear un addon de Odoo desde cero

Esta guía te mostrará cómo crear un addon de Odoo desde cero, configurarlo con Docker y activarlo en tu instancia de Odoo.

## 🛠️ Pasos para la creación del addon

1.  **📁 Estructura de carpetas:**
    *   Crea una carpeta raíz para tu proyecto.
    *   Dentro de ella, crea una carpeta vacía llamada `addons`. Aquí es donde residirá todo el código de tu addon.
    *   Dentro de `addons`, crea otra carpeta para tu addon (por ejemplo, `mi_nuevo_addon`).

2.  **📄 Archivos esenciales:**
    *   Dentro de la carpeta de tu addon, crea dos archivos:
        *   `__init__.py`: Déjalo vacío por ahora.
        *   `__manifest__.py`: Este archivo es crucial para que Odoo reconozca tu addon. Aquí tienes un ejemplo:

    ```python
    # __manifest__.py
    {
        'name': 'Mi Módulo Odoo Personalizado',
        'version': '1.0',
        'summary': 'Módulo de ejemplo para formularios personalizados en Odoo.',
        'sequence': 10,
        'description': """
            Este módulo demuestra cómo crear un modelo y formulario totalmente personalizado en Odoo.
        """,
        'category': 'Uncategorized',
        'depends': ['base'],
        'data': [],
        'views': [],
        'installable': True,
        'application': True,
        'auto_install': False,
        'license': 'LGPL-3',
    }
    ```

    Asegúrate de ajustar los valores a tus necesidades.

3.  **⚙️ Configuración de Odoo:**
    *   En la raíz de tu proyecto, crea un archivo `odoo.conf` con el siguiente contenido:

    ```ini
    [options]
    addons_path = /mnt/odoo/addons,/mnt/extra-addons
    data_dir = /var/lib/odoo
    db_host = db
    db_port = 5432
    db_user = odoo
    db_password = odoo
    admin_passwd = admin
    ```

4.  **🐳 Configuración de Docker:**
    *   Crea un archivo `docker-compose.yml` en la raíz de tu proyecto:

    ```yaml
    services:
      db:
        image: postgres:17.5-alpine3.22
        restart: always
        environment:
          POSTGRES_DB: testdbname
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
        volumes:
          - odoo-db-data:/var/lib/postgresql/data
        ports:
          - "5439:5432"
        networks:
          - odoo-net

      web:
        image: odoo:18.0
        depends_on:
          - db
        ports:
          - "8069:8069"
        volumes:
          - ./addons:/mnt/extra-addons
          - ./odoo.conf:/etc/odoo/odoo.conf
        environment:
          - HOST=db
          - USER=odoo
          - PASSWORD=odoo
        networks:
          - odoo-net
        command: >
          /usr/bin/odoo -c /etc/odoo/odoo.conf --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons

    networks:
      odoo-net:
    volumes:
      odoo-db-data:
      odoo-web-data:
    ```

    Asegúrate de que todos los nombres y variables coincidan con tu configuración.

5.  **🚀 Lanzamiento:**
    *   Levanta el proyecto con el comando: `docker-compose up --build`

## ✨ Cómo activar el addon

Una vez que tu instancia de Odoo esté en funcionamiento, sigue estos pasos para activar tu addon:

1.  **Accede a Odoo:** Abre tu navegador y ve a `http://localhost:8069`.
2.  **Activa el modo de desarrollador:**
    *   Ve a `Ajustes`.
    *   Busca la opción `Activar el modo de desarrollador` y haz clic en ella.
3.  **Actualiza la lista de aplicaciones:**
    *   Ve a `Aplicaciones`.
    *   En el menú, busca y haz clic en `Actualizar lista de aplicaciones`.
4.  **Busca y activa tu addon:**
    *   En la barra de búsqueda de `Aplicaciones`, elimina el filtro `Aplicaciones` para ver todos los módulos.
    *   Busca el nombre de tu addon (el que pusiste en el `__manifest__.py`).
    *   Haz clic en el botón `Activar`.

¡Y listo! 🎉 Tu addon ahora está activo y funcionando en tu instancia de Odoo.

## In emergency case
docker compose run --rm web \
  odoo -d odoo -i base --stop-after-init

sudo docker compose run --rm web \
  odoo -d odoo \
       -u client_basic_params \
       --stop-after-init

Iniciar db
docker compose run --rm web \
  odoo -d odoo -i base --stop-after-init \
  --without-demo=all --load-language=es_CL

### Borrar todo 
 1 - Para y elimina contenedores + volúmenes del compose actual
docker compose down --volumes --remove-orphans

 2 - Elimina TODOS los volúmenes que lleven “odoo” en el nombre
docker volume ls -q | grep odoo | xargs -r docker volume rm

 (opcional) 3 - Borra cualquier volumen “huérfano”
docker volume prune     # ENTER y confirma

 4 - Arranca de nuevo
docker compose up --build

docker exec -it odoo-addon-web-1 odoo shell -d odoo