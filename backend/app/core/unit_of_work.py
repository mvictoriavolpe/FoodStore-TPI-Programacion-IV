from sqlmodel import Session

from app.core.database import session_factory


class UnitOfWork:
    """One session and transaction shared by all repositories in an operation."""

    def __init__(self, factory=None):
        self.factory = factory or session_factory
        self.session: Session

    def __enter__(self):
        self.session = self.factory()
        try:
            # SQLite has no row locks. Serialize writers before their first read;
            # PostgreSQL uses SELECT FOR UPDATE in the repositories instead.
            if self.session.get_bind().dialect.name == "sqlite":
                self.session.connection().exec_driver_sql("BEGIN IMMEDIATE")
            self.setup_repositories()
            return self
        except BaseException:
            self.session.rollback()
            self.session.close()
            raise

    def setup_repositories(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                try:
                    self.session.commit()
                except BaseException:
                    self.session.rollback()
                    raise
            else:
                self.session.rollback()
        finally:
            self.session.close()
        return False
