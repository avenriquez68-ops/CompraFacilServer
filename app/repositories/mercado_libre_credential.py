"""Persistencia de credenciales OAuth de Mercado Libre."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.clients.mercado_libre_oauth import (
    MercadoLibreToken,
)
from app.models.mercado_libre_credential import (
    MercadoLibreCredentialModel,
)


class MercadoLibreCredentialRepository:
    """Guarda y actualiza credenciales de Mercado Libre."""

    def get_latest(
        self,
        session: Session,
    ) -> MercadoLibreCredentialModel | None:
        """Devuelve las credenciales actualizadas más recientemente."""

        statement = (
            select(MercadoLibreCredentialModel)
            .order_by(
                MercadoLibreCredentialModel.updated_at.desc(),
                MercadoLibreCredentialModel.id.desc(),
            )
            .limit(1)
        )

        return session.scalar(statement)

    def save(
        self,
        session: Session,
        token: MercadoLibreToken,
    ) -> MercadoLibreCredentialModel:
        """Guarda las credenciales vigentes de un usuario."""

        statement = select(
            MercadoLibreCredentialModel
        ).where(
            MercadoLibreCredentialModel.user_id
            == token.user_id
        )

        credential = session.scalar(statement)

        expires_at = datetime.now(
            timezone.utc
        ) + timedelta(seconds=token.expires_in)

        if credential is None:
            credential = MercadoLibreCredentialModel(
                user_id=token.user_id,
                access_token=token.access_token,
                refresh_token=token.refresh_token,
                token_type=token.token_type,
                scope=token.scope,
                expires_at=expires_at,
            )
            session.add(credential)
        else:
            credential.access_token = token.access_token
            credential.refresh_token = token.refresh_token
            credential.token_type = token.token_type
            credential.scope = token.scope
            credential.expires_at = expires_at

        session.commit()
        session.refresh(credential)

        return credential


mercado_libre_credential_repository = (
    MercadoLibreCredentialRepository()
)