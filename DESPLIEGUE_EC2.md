# Despliegue EC2 — 2 de noviembre de 2026

URL: http://3.217.227.197/

- Aplicación: /home/ubuntu/portal-eva3
- Servicio: portal-eva3.service (Gunicorn con 2 workers, habilitado al arranque).
- Apache: proxy HTTP a 127.0.0.1:8002; estáticos locales en /var/www/portal-static.
- Base existente MariaDB conservada: 2 noticias y 4 películas.
- Migración gestion.0001_initial aplicada para funciones y reservas.
- Roles configurados y tres cuentas de demostración creadas; claves entregadas en el chat, sin incluirlas en el código.
- DEBUG=False y hosts configurados para la IP pública.

## Verificado

Siete pruebas automatizadas aprobadas en el servidor usando base SQLite aislada. En la aplicación real con MariaDB se comprobó desde Internet login y dashboard de los tres perfiles, noticias, cine, reservas, formulario de reserva y acceso de usuarios (200 para Administrador, 403 para los otros perfiles). Bootstrap responde 200. Posteriormente se comprobó el envío SMTP real y el estudiante confirmó el cambio de contraseña.

## Respaldo previo

/home/ubuntu/backups/portal-20261102-205240/

Contiene previous-code.tar.gz, eva2_backend.sql y apache-default.conf. Acceso restringido. El código anterior permanece en /home/ubuntu/evalu2backend.

## Operación

```bash
sudo systemctl status portal-eva3
sudo journalctl -u portal-eva3 -n 80 --no-pager
sudo systemctl restart portal-eva3
sudo apache2ctl configtest
```

Gmail SMTP fue configurado y la recuperación fue confirmada por el estudiante. El informe técnico está en docs/Informe_Evaluacion3.pdf. Las capturas externas y los prompts se completarán posteriormente. La web actualmente utiliza HTTP; antes de utilizar cuentas o información real se debe configurar dominio y HTTPS. Las contraseñas locales no son las mismas que las de EC2.
