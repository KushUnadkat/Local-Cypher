import socket
import threading

class EnigmaMachine:
    def __init__(self, rotors, reflector, plugboard_pairs, ring_settings, initial_positions):
        self.rotors = rotors
        self.reflector = reflector
        self.plugboard = self.create_plugboard(plugboard_pairs)
        self.ring_settings = ring_settings
        self.positions = initial_positions
        self.alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def create_plugboard(self, pairs):
        plugboard = {letter: letter for letter in self.alphabet}
        for a, b in pairs:
            plugboard[a] = b
            plugboard[b] = a
        return plugboard

    def rotate_rotors(self):
        self.positions[0] = (self.positions[0] + 1) % 26
        if self.positions[0] == 0:
            self.positions[1] = (self.positions[1] + 1) % 26
            if self.positions[1] == 0:
                self.positions[2] = (self.positions[2] + 1) % 26

    def encipher_letter(self, letter):
        letter = self.plugboard[letter]
        index = self.alphabet.index(letter)
        for i, rotor in enumerate(self.rotors):
            index = (index + self.positions[i] - self.ring_settings[i]) % 26
            index = self.alphabet.index(rotor[index])
            index = (index - self.positions[i] + self.ring_settings[i]) % 26

        index = self.alphabet.index(self.reflector[index])

        for i, rotor in reversed(list(enumerate(self.rotors))):
            index = (index + self.positions[i] - self.ring_settings[i]) % 26
            index = rotor.index(self.alphabet[index])
            index = (index - self.positions[i] + self.ring_settings[i]) % 26

        letter = self.alphabet[index]
        letter = self.plugboard[letter]

        self.rotate_rotors()

        return letter

    def process_message(self, message):
        result = ''
        for letter in message:
            if letter in self.alphabet:
                result += self.encipher_letter(letter)
            else:
                result += letter
        return result

clients = []

def broadcast_message(message, exclude_client):
    for client in clients:
        if client != exclude_client:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)

def handle_client(client_socket):
    # Define the Enigma Machine configuration
    rotors = [
        'EKMFLGDQVZNTOWYHXUSPAIBRCJ',  # Rotor I
        'AJDKSIRUXBLHWTMCQGZNPYFVOE',  # Rotor II
        'BDFHJLCPRTXVZNYEIWGAKMUSQO'   # Rotor III
    ]
    reflector = 'YRUHQSLDPXNGOKMIEBFZCWVJAT'
    plugboard_pairs = [('A', 'M'), ('G', 'L'), ('E', 'T')]
    ring_settings = [1, 1, 1]
    initial_positions = [0, 0, 0]

    # Create an Enigma machine with the given configuration
    enigma = EnigmaMachine(rotors, reflector, plugboard_pairs, ring_settings, initial_positions)

    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            decoded_message = enigma.process_message(message.decode('utf-8'))
            broadcast_message(decoded_message.encode('utf-8'), client_socket)
        except:
            client_socket.close()
            clients.remove(client_socket)
            break

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server started on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        clients.append(client_socket)
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    host = "0.0.0.0"  # Listen on all interfaces
    port = int(input("Enter server port: "))
    start_server(host, port)
