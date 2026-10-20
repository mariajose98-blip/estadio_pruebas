"""Registro y gestión de patrocinadores.

Ruta real: POST /patrocinador/ con la clave 'registrar' en el form.
Campos: nombre_empresa, rif, tipo_contrato (1|2|3), nombre_contacto,
telefono, email y encargado_id (obligatorio).
"""
import uuid


def _filas(app, sql, params=()):
    with app.app_context():
        from app.database import Database
        with Database.get_connection('estadio_db').cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def _nombre():
    return f'Empresa Prueba {uuid.uuid4().hex[:8]}'


def _datos(encargado_id, nombre_empresa, **overrides):
    data = {
        'registrar': 'true',
        'nombre_empresa': nombre_empresa,
        'rif': 'J-12345678',
        'tipo_contrato': '1',
        'nombre_contacto': 'Carlos Mendoza',
        'telefono': '04121234567',
        'email': 'contacto@ejemplo.com',
        'encargado_id': str(encargado_id),
    }
    data.update(overrides)
    return data


def test_registrar_patrocinador_exitoso(app, client, superadmin):
    nombre = _nombre()
    resp = client.post('/patrocinador/', data=_datos(superadmin.id, nombre))

    assert resp.status_code == 200
    assert resp.get_json()['mensaje'] == 'Patrocinador registrado correctamente'

    filas = _filas(app, "SELECT * FROM patrocinadores WHERE nombre_empresa = %s", (nombre,))
    assert len(filas) == 1
    p = filas[0]
    assert p['rif'] == 'J-12345678'
    assert str(p['tipo_contrato']) == '1'
    assert p['nombre_contacto'] == 'Carlos Mendoza'
    assert p['email'] == 'contacto@ejemplo.com'
    assert p['encargado_id'] == superadmin.id
    assert p['estado'] == 1


def test_registrar_rif_invalido_no_persiste(app, client, superadmin):
    nombre = _nombre()
    resp = client.post('/patrocinador/', data=_datos(superadmin.id, nombre, rif='123'))

    assert resp.status_code == 200
    assert resp.get_json()['mensaje'] == 'Error al registrar el patrocinador'
    assert _filas(app, "SELECT COUNT(*) c FROM patrocinadores WHERE nombre_empresa = %s",
                  (nombre,))[0]['c'] == 0


def test_registrar_tipo_contrato_invalido_falla(client, superadmin):
    resp = client.post('/patrocinador/', data=_datos(superadmin.id, _nombre(), tipo_contrato='9'))

    assert resp.status_code == 400
    assert 'contrato' in resp.get_json()['error']


def test_registrar_duplicado_es_detectado(client, superadmin):
    nombre = _nombre()
    client.post('/patrocinador/', data=_datos(superadmin.id, nombre))

    resp = client.post('/patrocinador/', data={'verificar_nombre': nombre})
    assert resp.get_json()['existe'] is True


def test_sin_permiso_devuelve_403(client, crear_usuario):
    usuario = crear_usuario(rol='SinPermisos')
    with client.session_transaction() as s:
        s['_user_id'] = str(usuario.id)
        s['_fresh'] = True

    from flask import g
    g.pop('_login_user', None)

    resp = client.post('/patrocinador/', data=_datos(usuario.id, _nombre()))
    assert resp.status_code == 403
