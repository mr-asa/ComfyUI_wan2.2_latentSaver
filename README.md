# ComfyUI WAN 2.2 Latent Save/Load Nodes

## English

This package provides two server-side custom ComfyUI nodes for working with WAN 2.2 latents:

- `WAN2 Latent Save` — saves a latent to a specified file path.
- `WAN2 Latent Load` — loads a latent from a specified file path.

## Supported Formats

- `.pt`, `.pth`, `.latent` — PyTorch / serialized latent tensor
- `.npz` — NumPy archive with key `latent`
- `.npy` — NumPy array

## Installation

1. Copy the folder `src/wan2_latent_saver` into ComfyUI's `custom_nodes` directory.
2. Restart the ComfyUI server.
3. The nodes will appear under the `WAN 2.2` category.

## Usage

### Save

- Input `latent` — a latent tensor from a WAN 2.2 model.
- Input `path` — a file path string, e.g. `C:/latents/my_latent.pt`.

### Load

- Input `path` — path to the latent file.
- Output — a `LATENT` object that can be passed further through the graph.

## Structure

- `src/wan2_latent_saver/nodes.py` — node implementation.
- `src/wan2_latent_saver/__init__.py` — node mapping export.

## Notes

- The save directory is created automatically if it does not exist.
- `.latent` is supported as an alias for PyTorch-serialized latent files.
- When loading `.npz`, the `latent` key is used if present; otherwise the first array is loaded.

---

## Русский

Этот пакет содержит два серверных кастомных нода ComfyUI для работы с латентами WAN 2.2:

- `WAN2 Latent Save` — сохраняет латент на указанный путь.
- `WAN2 Latent Load` — загружает латент из указанного пути.

## Поддерживаемые форматы

- `.pt`, `.pth`, `.latent` — PyTorch / сериализованный латентный тензор
- `.npz` — NumPy архив с ключом `latent`
- `.npy` — NumPy массив

## Установка

1. Скопируйте папку `src/wan2_latent_saver` в каталог `custom_nodes` ComfyUI.
2. Перезапустите сервер ComfyUI.
3. Ноды появятся в категории `WAN 2.2`.

## Использование

### Сохранение

- Вход `latent` — латентное представление из модели WAN 2.2.
- Вход `path` — строка пути, например `C:/latents/my_latent.pt`.

### Загрузка

- Вход `path` — путь к файлу латента.
- Выход — объект `LATENT`, который можно передать дальше по графу.

## Структура

- `src/wan2_latent_saver/nodes.py` — реализация нод.
- `src/wan2_latent_saver/__init__.py` — экспорт маппингов нод.

## Примечания

- Директория для сохранения создаётся автоматически, если она не существует.
- `.latent` поддерживается как псевдоним для PyTorch-сериализованных латентов.
- При загрузке `.npz` используется поле `latent`, если оно есть; иначе берётся первый массив.
