import logging

_logger = logging.getLogger(__name__)

def _update_partner_names(env):
    """
    Intenta rellenar los campos first_name para los registros existentes
    tomando la primera palabra del campo 'name'.
    """
    _logger.info("Iniciando actualización de nombres de partners para client_basic_params.")
    
    # Obtenemos el cursor (cr) del entorno (env)
    cr = env.cr
    
    # Desactivamos el onchange para evitar problemas de sincronización
    cr.execute("""
        UPDATE res_partner
        SET first_name = split_part(name, ' ', 1)
        WHERE first_name IS NULL AND name IS NOT NULL;
    """)
    
    # Para los que queden nulos, ponemos un valor por defecto
    cr.execute("""
        UPDATE res_partner
        SET first_name = 'Sin Nombre'
        WHERE first_name IS NULL;
    """)
    
    _logger.info("Finalizada la actualización de nombres de partners.")