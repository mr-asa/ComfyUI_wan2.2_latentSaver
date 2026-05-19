import os
from pathlib import Path

import numpy as np
import torch


SUPPORTED_EXTENSIONS = (".pt", ".pth", ".latent", ".npz", ".npy")


class WAN2LatentSave:
    CATEGORY = "WAN 2.2"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "latent": ("LATENT",),
                "path": ("STRING",),
            }
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "save_latent"

    def save_latent(self, latent, path):
        save_path = self._normalize_path(path)
        tensor = self._normalize_latent(latent)
        tensor = tensor.detach().cpu()

        self._save_tensor(tensor, save_path)
        return (tensor,)

    def _normalize_path(self, path):
        if not isinstance(path, str) or not path.strip():
            raise ValueError("Path must be a non-empty string.")

        expanded = os.path.expanduser(path)
        resolved = Path(expanded)

        if resolved.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Unsupported extension for latent save. Use .pt, .pth, .latent, .npz or .npy."
            )

        if resolved.is_dir():
            raise ValueError("Path must point to a file, not a directory.")

        resolved.parent.mkdir(parents=True, exist_ok=True)
        return resolved

    def _normalize_latent(self, latent):
        if isinstance(latent, torch.Tensor):
            return latent

        if isinstance(latent, np.ndarray):
            return torch.from_numpy(latent)

        if isinstance(latent, (list, tuple)):
            return torch.tensor(latent)

        raise TypeError(
            f"Unsupported latent type {type(latent).__name__}. Expected a torch.Tensor, numpy.ndarray, list или tuple."
        )

    def _save_tensor(self, tensor, path: Path):
        ext = path.suffix.lower()
        if ext in (".pt", ".pth"):
            torch.save(tensor, path)
            return

        if ext == ".npz":
            np.savez_compressed(path, latent=tensor.numpy())
            return

        if ext == ".npy":
            np.save(path, tensor.numpy())
            return

        raise ValueError("Unsupported file extension for latent save.")


class WAN2LatentLoad:
    CATEGORY = "WAN 2.2"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "path": ("STRING",),
            }
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "load_latent"

    def load_latent(self, path):
        load_path = self._normalize_path(path)
        ext = load_path.suffix.lower()

        if ext in (".pt", ".pth", ".latent"):
            latent = torch.load(load_path, map_location="cpu")
            latent = self._extract_latent_object(latent)
        elif ext == ".npz":
            latent = self._load_npz(load_path)
        elif ext == ".npy":
            latent = np.load(load_path)
        else:
            raise ValueError(
                "Unsupported extension for latent load. Use .pt, .pth, .latent, .npz or .npy."
            )

        if isinstance(latent, np.ndarray):
            latent = torch.from_numpy(latent)

        if not isinstance(latent, torch.Tensor):
            raise TypeError(
                f"Loaded latent has unsupported type {type(latent).__name__}."
            )

        return (latent,)

    def _normalize_path(self, path):
        if not isinstance(path, str) or not path.strip():
            raise ValueError("Path must be a non-empty string.")

        expanded = os.path.expanduser(path)
        resolved = Path(expanded)

        if not resolved.exists():
            raise FileNotFoundError(f"Latent file not found: {resolved}")

        if resolved.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Unsupported extension for latent load. Use .pt, .pth, .npz or .npy."
            )

        return resolved

    def _extract_latent_object(self, latent):
        if isinstance(latent, dict) and "latent" in latent:
            return latent["latent"]
        return latent

    def _load_npz(self, path: Path):
        archive = np.load(path)
        if "latent" in archive:
            return archive["latent"]

        values = list(archive.values())
        if not values:
            raise ValueError("NPZ archive does not contain any arrays.")
        return values[0]


NODE_CLASS_MAPPINGS = {
    "WAN2 Latent Save": WAN2LatentSave,
    "WAN2 Latent Load": WAN2LatentLoad,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WAN2 Latent Save": "WAN2 Latent Save",
    "WAN2 Latent Load": "WAN2 Latent Load",
}
