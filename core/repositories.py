def aplicar_cambios(instancia, **cambios):
    """Asigna los campos y guarda solo esos."""
    for campo, valor in cambios.items():
        setattr(instancia, campo, valor)
    if cambios:
        instancia.save(update_fields=list(cambios))
    return instancia