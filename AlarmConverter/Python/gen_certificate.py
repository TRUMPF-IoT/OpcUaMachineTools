# MIT License

# Copyright (c) 2022 TRUMPF Werkzeugmaschinen SE + Co. KG

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import datetime

def get_application_uri(hostname, applicationName):
    return f"urn:{hostname}:freeopcua:{applicationName}"


def gen_certificates(privateKeyFullPath, certificateFullPath, hostname, applicationName):

    # Generate the key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    privateKeyBytes = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

    # Write our key to disk for safe keeping
    if (privateKeyFullPath):
        with open(privateKeyFullPath, "wb") as f:
            f.write(privateKeyBytes)
    
    # Various details about who we are. For a self-signed certificate the
    # subject and issuer are always the same.
    # Did not set country, state and locality
    # https://cryptography.io/en/latest/x509/reference.html
    # https://cryptography.io/en/latest/x509/reference.html#general-name-classes
    # https://cryptography.io/en/latest/x509/reference.html#x-509-extensions    
    theName = f"{applicationName}@{hostname}"
    serialNumber = x509.random_serial_number()
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.LOCALITY_NAME, applicationName),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, f"{applicationName}_Organization"),       
        x509.NameAttribute(NameOID.COMMON_NAME, theName),
       ])
   
    # Create early, so that ski.digest can be used in the certificate builder
    ski = x509.SubjectKeyIdentifier.from_public_key(key.public_key())    
 
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(serialNumber)
        # Start validity period from yesterday
        .not_valid_before(datetime.datetime.today() - datetime.timedelta(days=1))
        # Our certificate will be valid for 10 years
        .not_valid_after(datetime.datetime.utcnow() + (datetime.timedelta(days=365)*10))
        # -------------------------------------------------------------------------------------------------
        # If an extension is marked as critical (critical True), it can not be ignored by an application.
        # The application must recognise and process the extension.
        # -------------------------------------------------------------------------------------------------
        .add_extension(
            # The subject key identifier extension provides a means of identifying 
            # certificates that contain a particular public key.         
            ski, critical=False)
        .add_extension(
            # The authority key identifier extension provides a means of 
            # identifying the public key corresponding to the private key used to sign a certificate.                      
            x509.AuthorityKeyIdentifier(ski.digest, [x509.DirectoryName(issuer)], serialNumber), critical=False)
        # Subject alternative name is an X.509 extension that provides a list of general name instances 
        # that provide a set of identities for which the certificate is valid.
        .add_extension(
            x509.SubjectAlternativeName([ 
                # URI must be first entry of SubjectAlternativeName. Must exactly match the client.application_uri 
                x509.UniformResourceIdentifier(get_application_uri(hostname, applicationName)),             
                x509.DNSName(hostname)                                        
                ]), critical=False)                
        # The key usage extension defines the purpose of the key contained in the certificate.
        .add_extension(
            # Basic constraints is an X.509 extension type that defines whether a given certificate is 
            # allowed to sign additional certificates and what path length restrictions may exist.            
            x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True, content_commitment=True, key_encipherment=True, 
                data_encipherment=True, key_agreement=False, key_cert_sign=True, crl_sign=False, 
                encipher_only=False, decipher_only=False), critical=True)
        .add_extension(
            # This extension indicates one or more purposes for which the certified public key may be used, 
            # in addition to or in place of the basic purposes indicated in the key usage extension.
            x509.ExtendedKeyUsage([x509.OID_SERVER_AUTH, x509.OID_CLIENT_AUTH]), critical=True)      
        # Sign our certificate with our private key
        .sign(key, algorithm=hashes.SHA256()))
    
    certificateBytes = cert.public_bytes(serialization.Encoding.DER)

    if (certificateFullPath):
        with open(certificateFullPath, "wb") as f:
            f.write(certificateBytes)

    return (privateKeyBytes, certificateBytes)