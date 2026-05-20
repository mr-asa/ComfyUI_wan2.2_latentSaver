import os
from pathlib import Path

import numpy as np
import torch


SUPPORTED_EXTENSIONS = (".pt", ".pth", ".latent", ".npz", ".npy")
DEFAULT_EXTENSION = ".pt"

# Relative (non-absolute) paths are interpreted relative to ComfyUI's
# `output` folder. This keeps files physically in the repo root by
# default while showing them as part of the output/catalog in the UI.
DEFAULT_OUTPUTS_DIR = Path(os.getcwd()) / "output"


class WAN2LatentSave:
    CATEGORY = "mr-asa/WAN 2.2"
    DESCRIPTION = "Save a WAN 2.2 latent tensor to disk. Supports .pt/.pth/.latent/.npz/.npy."
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "latent": ("LATENT", {"display_name": "Latent", "tooltip": "WAN 2.2 latent tensor to save."}),
                "path": (
                    "STRING",
                    {
                        "display_name": "File path",
                        "placeholder": "C:/latents/my_latent.pt",
                        "tooltip": "File path where the latent will be saved. Supported extensions: .pt, .pth, .latent, .npz, .npy.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent",)
    OUTPUT_TOOLTIPS = ("Saved latent tensor",)
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
        candidate = Path(expanded)

        # If the path is not absolute, treat it as relative to the outputs folder
        if not candidate.is_absolute():
            candidate = DEFAULT_OUTPUTS_DIR / candidate

        # If user provided a folder-only path without filename/extension,
        # require a filename (we don't invent names). If candidate looks like
        # a directory, error.
        if str(path).endswith(("/", "\\")) or candidate.name == "":
            raise ValueError("Path must include a filename, not only a directory.")

        # If no extension provided, choose the default format
        if not candidate.suffix:
            candidate = candidate.with_suffix(DEFAULT_EXTENSION)

        if candidate.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Unsupported extension for latent save. Use .pt, .pth, .latent, .npz or .npy."
            )

        candidate.parent.mkdir(parents=True, exist_ok=True)
        return candidate

    def _normalize_latent(self, latent):
        if isinstance(latent, dict):
            latent = self._extract_latent_object(latent)

        if isinstance(latent, torch.Tensor):
            return latent

        if isinstance(latent, np.ndarray):
            return torch.from_numpy(latent)

        if isinstance(latent, (list, tuple)):
            return torch.tensor(latent)

        raise TypeError(
            f"Unsupported latent type {type(latent).__name__}. Expected a torch.Tensor, numpy.ndarray, list или tuple."
        )

    def _extract_latent_object(self, latent):
        if isinstance(latent, (torch.Tensor, np.ndarray, list, tuple)):
            return latent

        if not isinstance(latent, dict):
            return latent

        if "latent" in latent:
            return self._extract_latent_object(latent["latent"])
        if "tensor" in latent:
            return self._extract_latent_object(latent["tensor"])
        if "data" in latent:
            return self._extract_latent_object(latent["data"])

        if len(latent) == 1:
            return self._extract_latent_object(next(iter(latent.values())))

        for value in latent.values():
            extracted = self._extract_latent_object(value)
            if isinstance(extracted, (torch.Tensor, np.ndarray, list, tuple)):
                return extracted

        return latent

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
    CATEGORY = "mr-asa/WAN 2.2"
    DESCRIPTION = "Load a WAN 2.2 latent tensor from disk. Supports .pt/.pth/.latent/.npz/.npy. Optionally wrap the result as a WanVideoSampler-compatible samples dict."

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "path": (
                    "STRING",
                    {
                        "display_name": "File path",
                        "placeholder": "C:/latents/my_latent.pt",
                        "tooltip": "Path to an existing latent file. Supported extensions: .pt, .pth, .latent, .npz, .npy.",
                    },
                ),
            },
            "optional": {
                "wrap_for_wan_video": (
                    "BOOLEAN",
                    {
                        "display_name": "WanVideoSampler compatibility",
                        "tooltip": "If enabled, wrap the loaded latent in a dict with key 'samples' for WanVideoWrapper sampler compatibility.",
                    },
                ),
            },
        }

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent",)
    OUTPUT_TOOLTIPS = ("Loaded latent tensor or WanVideoSampler-compatible samples dict",)
    FUNCTION = "load_latent"

    def load_latent(self, path, wrap_for_wan_video=False):
        load_path = self._normalize_path(path)
        ext = load_path.suffix.lower()

        if ext in (".pt", ".pth", ".latent"):
            loaded = torch.load(load_path, map_location="cpu")
        elif ext == ".npz":
            loaded = self._load_npz(load_path)
        elif ext == ".npy":
            loaded = np.load(load_path)
        else:
            raise ValueError(
                "Unsupported extension for latent load. Use .pt, .pth, .latent, .npz or .npy."
            )

        if wrap_for_wan_video:
            result = self._wrap_for_wan_video(loaded)
            return (result,)

        latent = self._extract_latent_object(loaded)
        if isinstance(latent, np.ndarray):
            latent = torch.from_numpy(latent)

        if not isinstance(latent, torch.Tensor):
            raise TypeError(
                f"Loaded latent has unsupported type {type(latent).__name__}."
            )

        return (latent,)

    def _wrap_for_wan_video(self, loaded):
        if isinstance(loaded, dict):
            if "samples" in loaded:
                return loaded

            samples = self._extract_latent_object(loaded)
            if isinstance(samples, np.ndarray):
                samples = torch.from_numpy(samples)
            if isinstance(samples, (list, tuple)):
                samples = torch.tensor(samples)

            result = {"samples": samples}
            for key, value in loaded.items():
                if key not in {"latent", "tensor", "data"}:
                    result[key] = value
            return result

        if isinstance(loaded, np.ndarray):
            return {"samples": torch.from_numpy(loaded)}

        if isinstance(loaded, torch.Tensor):
            return {"samples": loaded}

        if isinstance(loaded, (list, tuple)):
            return {"samples": torch.tensor(loaded)}

        raise TypeError(
            f"Loaded latent has unsupported type {type(loaded).__name__} for WanVideoSampler wrapping."
        )

    def _normalize_path(self, path):
        if not isinstance(path, str) or not path.strip():
            raise ValueError("Path must be a non-empty string.")

        expanded = os.path.expanduser(path)
        candidate = Path(expanded)

        # If not absolute, look in the outputs folder first
        if not candidate.is_absolute():
            candidate = DEFAULT_OUTPUTS_DIR / candidate

        # If no extension was provided, try to find a matching file by
        # checking supported extensions in preferred order.
        if not candidate.suffix:
            for ext in (".pt", ".pth", ".latent", ".npz", ".npy"):
                cand = candidate.with_suffix(ext)
                if cand.exists():
                    return cand
            raise FileNotFoundError(f"Latent file not found (tried supported extensions) for base: {candidate}")

        if not candidate.exists():
            raise FileNotFoundError(f"Latent file not found: {candidate}")

        if candidate.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Unsupported extension for latent load. Use .pt, .pth, .npz or .npy."
            )

        return candidate

    def _extract_latent_object(self, latent):
        if isinstance(latent, (torch.Tensor, np.ndarray, list, tuple)):
            return latent

        if not isinstance(latent, dict):
            return latent

        if "latent" in latent:
            return self._extract_latent_object(latent["latent"])
        if "tensor" in latent:
            return self._extract_latent_object(latent["tensor"])
        if "data" in latent:
            return self._extract_latent_object(latent["data"])

        if len(latent) == 1:
            return self._extract_latent_object(next(iter(latent.values())))

        for value in latent.values():
            extracted = self._extract_latent_object(value)
            if isinstance(extracted, (torch.Tensor, np.ndarray, list, tuple)):
                return extracted

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
