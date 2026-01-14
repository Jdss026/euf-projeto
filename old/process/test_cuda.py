import torch
print(f"Versão: {torch.__version__}")
print(f"Dispositivo: {torch.cuda.get_device_name(0)}")
print(f"Capacidade: {torch.cuda.get_device_capability(0)}") # Deve retornar (6, 1)
