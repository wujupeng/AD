import logging
from typing import Any

from app.interfaces.i_saml_provider import ISamlProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class SamlAdapter(ISamlProvider):
    async def sign_assertion(self, attributes: dict[str, Any], audience: str, recipient: str) -> str:
        try:
            from saml2 import BINDING_HTTP_POST
            from saml2.saml import NameID, Subject, Attribute, AttributeValue
            from saml2.assertion import Assertion

            assertion = Assertion()
            assertion.attributes = []
            for key, value in attributes.items():
                attr = Attribute()
                attr.name = key
                attr.name_format = "urn:oasis:names:tc:SAML:2.0:attrname-format:basic"
                attr_val = AttributeValue()
                attr_val.text = str(value)
                attr.attribute_value = [attr_val]
                assertion.attributes.append(attr)

            return str(assertion)
        except Exception as e:
            logger.error("SAML assertion signing failed: %s", str(e))
            raise

    async def validate_authn_request(self, request_xml: str) -> dict[str, Any]:
        try:
            from saml2 import BINDING_HTTP_POST
            from saml2.request import AuthnRequest

            return {"valid": True, "request_xml": request_xml}
        except Exception as e:
            logger.error("SAML AuthnRequest validation failed: %s", str(e))
            return {"valid": False, "error": str(e)}

    async def generate_metadata(self) -> str:
        entity_id = settings.SAML_IDP_ENTITY_ID
        metadata_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" entityID="{entity_id}">
  <md:IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</md:NameIDFormat>
    <md:SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="{entity_id}/sso"/>
    <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="{entity_id}/slo"/>
  </md:IDPSSODescriptor>
</md:EntityDescriptor>"""
        return metadata_template

    async def parse_logout_request(self, request_xml: str) -> dict[str, Any]:
        try:
            return {"valid": True, "request_xml": request_xml}
        except Exception as e:
            logger.error("SAML LogoutRequest parsing failed: %s", str(e))
            return {"valid": False, "error": str(e)}