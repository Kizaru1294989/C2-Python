import os
import subprocess
import platform
import shutil


class SSLKeyGenerator:
    def __init__(self):
        self.green = "\x1b[32m"
        self.blue = "\x1b[34m"
        self.red = "\x1b[31m"
        self.orange = "\x1b[38;5;220m"
        self.Key = "SSL"

    def check_OpenSSL(self, os_type):
        # print(os_type)
        if os_type == "Linux":
            try:
                output = os.popen("openssl version").read()
                if output.split(" ")[0] in ["LibreSSL", "OpenSSL"]:
                    print(" [✅] OpenSSL is installed")
                    return True
                else:
                    print(f"{self.red} [❌] Error SSL\n     Try 'sudo apt install openssl'")
                    exit(0)
            except Exception as e:
                print(f"{self.red} [-] Error SSL\n     {e}\n     Try 'sudo apt install openssl'")
                exit(0)
        else:
            result = subprocess.run(["openssl", "version"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                output = result.stdout.strip()
                print(output)
                if output.split(" ")[0] in ["LibreSSL", "OpenSSL"]:
                    print(" ✅ OpenSSL is installed")
                    return True
                else:
                    print("OPEN SSL not installed")
                    exit(0)
            else:
                print("You need to install OPEN SSL")
                exit(0)

    def check_platform(self):
        return platform.system()

    def key_generation(self, os_local):
        print("OS: " + os_local)
        if os_local == "Linux":
            openssl_config_path = "/etc/ssl/openssl.cnf"
        elif os_local == "Windows":
            openssl_config_path = r"C:\xampp\apache\conf\openssl.cnf"
        else:
            print(f"{self.orange} [❌] Unsupported OS: {os_local}")
            return

        if not os.path.exists(self.Key):
            os.mkdir(self.Key)
            print(f"{self.orange} [✅] {self.Key} directory created")
            os.mkdir(os.path.join(self.Key, "CA"))
            os.mkdir(os.path.join(self.Key, "CERT"))
            print(f"{self.orange} [✅] CA and CERT directories created in {self.Key}")

            try:
                subprocess.run(
                    ["openssl", "genrsa", "-aes256", "-out", f"{self.Key}/CA/ca-key.pem", "4096"], check=True
                )
                print(f"{self.orange} [✅] CA private key generated")
            except subprocess.CalledProcessError as e:
                print(f"{self.orange} ❌ Error generating CA private key: {e}")

            try:
                subprocess.run(
                    [
                        "openssl",
                        "req",
                        "-new",
                        "-x509",
                        "-sha256",
                        "-days",
                        "365",
                        "-key",
                        f"{self.Key}/CA/ca-key.pem",
                        "-out",
                        f"{self.Key}/CA/ca-cert.pem",
                        "-config",
                        openssl_config_path,
                    ],
                    check=True,
                )
                print(f"{self.orange} [✅] CA certificate generated")
            except subprocess.CalledProcessError as e:
                print(f"{self.orange} [❌] Error generating CA certificate: {e}")

            try:
                subprocess.run(
                    ["openssl", "genrsa", "-out", f"{self.Key}/CERT/cert-key.pem", "4096"], check=True
                )
                print(f"{self.orange} [✅] Server private key generated")
            except subprocess.CalledProcessError as e:
                print(f"{self.orange} [❌] Error generating server private key: {e}")

            try:
                subprocess.run(
                    [
                        "openssl",
                        "req",
                        "-new",
                        "-sha256",
                        "-subj",
                        "/CN=esgi.com",
                        "-key",
                        f"{self.Key}/CERT/cert-key.pem",
                        "-out",
                        f"{self.Key}/CERT/cert-query.csr",
                        "-config",
                        openssl_config_path,
                    ],
                    check=True,
                )
                print(f"{self.orange} [✅] Certificate request generated")
            except subprocess.CalledProcessError as e:
                print(f"{self.orange} [❌] Error generating certificate request: {e}")

            try:
                with open(f"{self.Key}/CERT/extfile.cnf.txt", "w") as f:
                    input_ip = input("Enter server side IP: ")
                    print(f"IP server socket = {input_ip}")
                    f.write(f"subjectAltName=IP:{input_ip}\n")
                print(f"{self.orange} [✅] extfile.cnf.txt generated")
            except Exception as e:
                print(f"{self.orange} [❌] Error generating extfile.cnf.txt: {e}")

            try:
                subprocess.run(
                    [
                        "openssl",
                        "x509",
                        "-req",
                        "-sha256",
                        "-days",
                        "365",
                        "-in",
                        f"{self.Key}/CERT/cert-query.csr",
                        "-CA",
                        f"{self.Key}/CA/ca-cert.pem",
                        "-CAkey",
                        f"{self.Key}/CA/ca-key.pem",
                        "-out",
                        f"{self.Key}/CERT/cert-server.pem",
                        "-extfile",
                        f"{self.Key}/CERT/extfile.cnf.txt",
                        "-CAcreateserial",
                    ],
                    check=True,
                )
                print(f"{self.orange} [✅] Certificate signed by CA")
                print(f"{self.blue} DONE")
            except subprocess.CalledProcessError as e:
                print(f"{self.orange} [❌] Error signing certificate by CA: {e}")
        else:
            print(f"{self.orange} [✅] {self.Key} directory already exists")
            if os_local == "Linux":
                ssl_directory = "/home/rais/Dev/SpyWare/SSL"
                if os.path.exists(ssl_directory):
                    shutil.rmtree(ssl_directory)
                    print(f"{self.orange} [✅] SSL directory {ssl_directory} has been removed")
                    self.key_generation(os_local)
            elif os_local == "Windows":
                ssl_directory = "./SSL"
                shutil.rmtree(ssl_directory)
                self.key_generation(os_local)
            else:
                print(f"{self.orange} [❌] Unsupported OS: {os_local}")

    def os_check(self):
        current_platform = self.check_platform()
        if current_platform == "Windows":
            print("Windows")
            return "Windows"
        elif current_platform == "Linux":
            print("Linux")
            return "Linux"

        else:
            return None

    def init(self):
        print("Keys generation Initialisation")
        os_local = self.os_check()
        if self.check_OpenSSL(os_local):
            self.key_generation(os_local)
        else:
            print("❌")


def start_generation():
    generator = SSLKeyGenerator()
    generator.init()


if __name__ == "__main__":
    start_generation()
