from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "favorites": [item.serialize() for item in self.favorites]
        }


class People(db.Model):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="people", uselist=True, foreign_keys="Favorite.people_id")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Planet(db.Model):
    __tablename__ = "planet"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="planet", uselist=True, foreign_keys="Favorite.planet_id")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Favorite(db.Model):
    __tablename__ = "favorite"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    people_id: Mapped[int] = mapped_column(
        ForeignKey("people.id"), nullable=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("planet.id"), nullable=True)

    user: Mapped["User"] = relationship(back_populates="favorites")
    people: Mapped["People"] = relationship(
        back_populates="favorites", uselist=False, foreign_keys=[people_id])
    planet: Mapped["Planet"] = relationship(
        back_populates="favorites", uselist=False, foreign_keys=[planet_id])

    def serialize(self):
        return {
            "id": self.id,
            "people": self.people.serialize() if self.people else None,
            "planet": self.planet.serialize() if self.planet else None
        }
        # data = {
        #     "id": self.id,
        #     "user_id": self.user_id,
        # }
        # if self.people:
        #     data["people"] = self.people.serialize()
        # if self.planet:
        #     data["planet"] = self.planet.serialize()
        # return dict(sorted(data.items()))
