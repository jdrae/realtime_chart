class DBRouter:
    def db_for_read(self, model, **hints):
        if not hasattr(model.Meta, "_db"):
            return "default"
        return getattr(model.Meta, "_db", "default")

    def db_for_write(self, model, **hints):
        if not hasattr(model.Meta, "_db"):
            return "default"
        return getattr(model.Meta, "_db", "default")
