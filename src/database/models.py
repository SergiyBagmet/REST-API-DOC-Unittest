from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, Date, DateTime, func


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'contacts'

    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column('first_name', String(150), index=True)
    last_name: Mapped[str] = mapped_column('last_name', String(150), index=True)
    email: Mapped[str] = mapped_column('email', String(150), index=True)
    phone_number: Mapped[str] = mapped_column('phone_number', String(20))
    birthday: Mapped[Date] = mapped_column('birthday', Date)

    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updated_at', DateTime, default=None, onupdate=func.now())

    def __repr__(self) -> str:
        return (f'Contact('
                f'id={self.id}, '
                f'first_name={self.first_name}, '
                f'last_name={self.last_name}, '
                f'email={self.email}, '
                f'phone_number={self.phone_number}, '
                f'birthday={self.birthday}, '
                f'created_at={self.created_at}, '
                f'updated_at={self.updated_at})')

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'
