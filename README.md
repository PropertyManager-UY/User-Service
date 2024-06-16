# User Service

Este repositorio contiene el código fuente y los archivos necesarios para desplegar y ejecutar un servicio de gestion de usuarios y sesiones en un clúster de Kubernetes.

## Descripción

El servicio de usuario se de dica a la gestion de los datos de usuario y al inicio y cierre de sesiones de los mismos para que estos accedan al resto de servicios del Proyecto.

## Índice

- [Proceso de Despliegue](#proceso-de-despliegue)
- [Uso del Servicio](#uso-del-servicio)
  - [Funcionalidades Principales](#funcionalidades-principales)
    - [Registro de Usuarios](#registro-de-usuarios)
    - [Registro de Miembros de Inmobiliaria](#registro-de-miembros-de-inmobiliaria)
    - [Inicio de Sesión](#inicio-de-sesión)
    - [Cierre de Sesión](#cierre-de-sesión)
    - [Eliminación de Usuarios](#eliminación-de-usuarios)
    - [Actualización de Usuarios](#actualización-de-usuarios)
    - [Obtener Todos los Usuarios](#obtener-todos-los-usuarios)
    - [Obtener Usuarios por Inmobiliaria](#obtener-usuarios-por-inmobiliaria)
- [Versiones Disponibles](#versiones-disponibles)
- [Contribución](#contribución)

## Proceso de Despliegue

Para desplegar el servicio de gateway en un clúster de Kubernetes, sigue los siguientes pasos:

1. **Configuración de Secrets para el servicio:** Crea un Secret en el clúster que contenga los siguientes datos:
   - `AUTH_COLLECTION`: Nombre para la colección de usuarios dentro de la base de datos de MongoDB.
   - `DATABASE_NAME`: Nombre para la base de datos del proyecto.
   - `JWT_SECRET_KEY`: Clave con la que se cifra los datos de usuario para asegurarse de que estos no sean atrapados durante el flujo de navegación.
   - `MONGO_URI`: URL del servidor de DB dentro del clúster.
   - `REDIS_HOST`: Nombre de Host de REDIS dentro del clúster.
   - `REDIS_PORT`: Puerto de REDIS dentro del clúster.
   - `SECRET_KEY`: Clave usada para firmar las sesiones y asegurar que los datos de la misma no sean modificados.
   - `SESSION_KEY_PREFIX`: Prefijo para que las sesiones de distintas aplicaciones no colicionen dentro del servidor de REDIS.
   - `TEST_DATABASE_NAME`: Nombre para la base de datos de pruebas.

2. **Configuración de Variables de Entorno:** Define las siguientes variables de entorno en tu flujo de trabajo de GitHub Actions o en tu entorno local:
   - `DOCKER_USERNAME`: Nombre de usuario de Docker Hub.
   - `DOCKER_PASSWORD`: Contraseña de Docker Hub.
   - `K8_NAMESPACE`: Nombre del namespace de Kubernetes donde se desplegará el servicio.
   - `K8_DEPLOYMENT`: Nombre del deployment de Kubernetes.
   - `K8_SECRET`: Nombre del secret donde se encuentran los datos del clúster.
   - `HPA_NAME`: Nombre del HPA (Horizontal Pod Autoscaler).
   - `SERVICE_NAME`: Nombre del servicio de Kubernetes.
   - `K8_APP`: Nombre de la aplicación.

3. **Ejecución del Flujo de Trabajo:** Ejecuta el flujo de trabajo de GitHub Actions `deploy.yml`. Este flujo de trabajo construirá la imagen del contenedor, la subirá a Docker Hub y luego aplicará los recursos de Kubernetes necesarios en el clúster.

4. **Verificación del Despliegue:** Una vez completado el flujo de trabajo, verifica que el servicio de gateway esté desplegado correctamente en tu clúster de Kubernetes.

## Uso del Servicio

El Servicio de Gestión de Usuarios es una API RESTful diseñada para manejar la autenticación, autorización y gestión de usuarios en una aplicación inmobiliaria. La API permite registrar usuarios, autenticar inicios de sesión, gestionar roles, y manejar la pertenencia de usuarios a diferentes inmobiliarias. Este servicio está construido utilizando Flask, una biblioteca de microframework de Python, y MongoDB para la persistencia de datos.

### Funcionalidades Principales:

#### Registro de Usuarios
- **Ruta**: /register
- **Método**: POST
- **Descripción**: Registra un nuevo usuario con un nombre de usuario, contraseña, correo electrónico y rol. La ruta valida que el correo electrónico esté bien estructurado y asegura que no exista ya un usuario con el mismo nombre de usuario o correo electrónico.
- **Datos del Request**:
```
{
  "username": "exampleuser",
  "password": "securepassword",
  "email": "user@example.com",
  "role": "owner"
}
```

#### Registro de Miembros de Inmobiliaria
- **Ruta**: /register_member/<id_inmobiliaria>
- **Método**: POST
- **Descripción**: Permite a los administradores y propietarios registrar nuevos miembros en una inmobiliaria específica. La ruta asegura que el usuario no exista ya en la inmobiliaria.
- **Datos del Request**:
```
{
  "username": "newmember",
  "password": "securepassword",
  "email": "member@example.com",
  "role": "agente"
}
```

#### Inicio de Sesión
- **Ruta**: /login
- **Método**: POST
- **Descripción**: Autentica a un usuario utilizando su correo electrónico y contraseña, generando un token de acceso para la sesión.
- **Datos del Request**:
```
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Cierre de Sesión
- **Ruta**: /logout
- **Método**: POST
- **Descripción**: Cierra la sesión del usuario, limpiando el token de acceso de la sesión.

#### Eliminación de Usuarios
- **Ruta**: /delete
- **Método**: DELETE
- **Descripción**: Permite a los administradores y a los usuarios eliminar sus propias cuentas.
- **Datos del Request**:
```
{
  "user_id": "user123"
}
```

#### Actualización de Usuarios
- **Ruta**: /update/<user_id>
- **Método**: PUT
- **Descripción**: Permite a los administradores y a los propios usuarios actualizar sus datos. Solo los administradores pueden cambiar el id_inmobiliaria.
- **Datos del Request**:
```
{
  "password": "newpassword",
  "email": "newemail@example.com",
  "role": "owner",
  "id_inmobiliaria": "new_id_inmobiliaria"
}
```

#### Obtener Todos los Usuarios
- **Ruta**: /users
- **Método**: GET
- **Descripción**: Permite a los administradores obtener una lista de todos los usuarios registrados.

#### Obtener Usuarios por Inmobiliaria
- **Ruta**: /users/inmobiliaria/<id_inmobiliaria>
- **Método**: GET
- **Descripción**: Permite a los administradores y miembros de la inmobiliaria obtener una lista de usuarios pertenecientes a una inmobiliaria específica.

Este servicio proporciona una base sólida para la gestión de usuarios en aplicaciones inmobiliarias, asegurando que solo usuarios autenticados y autorizados puedan realizar acciones específicas y manteniendo la seguridad de los datos de los usuarios.

## Versiones Disponibles

- **latest:** Última versión estable del servicio. Se recomienda su uso para entornos de producción.
- **v1.0:** Versión inicial del servicio.

Para cambiar la versión del servicio, modifica la etiqueta de imagen del contenedor en el archivo `deploy.yml` antes de ejecutar el flujo de trabajo.

## Contribución

Si deseas contribuir a este proyecto, sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama para tu contribución (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commits (`git commit -am 'Agrega nueva funcionalidad'`).
4. Sube tus cambios a tu repositorio remoto (`git push origin feature/nueva-funcionalidad`).
5. Crea un nuevo pull request en GitHub.

Esperamos tus contribuciones!

