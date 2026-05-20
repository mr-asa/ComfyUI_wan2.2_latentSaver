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

1. Copy the root folder of this repository into ComfyUI's `custom_nodes` directory.
2. Restart the ComfyUI server.
3. The nodes will appear under the `mr-asa/WAN 2.2` category.

## Usage

### Save

- Input `latent` — a latent tensor from a WAN 2.2 model.
- Input `path` — a file path string, e.g. `C:/latents/my_latent.pt`.
- Node descriptions and input tooltips are available in the ComfyUI node editor.

### Load

- Input `path` — path to the latent file.
- Optional `wrap_for_wan_video` — wrap the loaded latent in a WanVideoSampler-compatible samples dict.
- Output — a `LATENT` object or WanVideoSampler-compatible samples dict that can be passed further through the graph.

## Structure

- `mr-asa/wan2_latent_saver/nodes.py` — node implementation.
- `mr-asa/wan2_latent_saver/__init__.py` — node mapping export.

## Notes

- The save directory is created automatically if it does not exist.
- `.latent` is supported as an alias for PyTorch-serialized latent files.
- File path placeholders and tooltips are available in the node editor.
- `WAN2 Latent Save` is marked as an output node and can be queued manually from the ComfyUI UI.
- When loading `.npz`, the `latent` key is used if present; otherwise the first array is loaded.

### Relative paths and default format

- If you provide a relative path or just a filename (for example `my_latent` or `folder/my_latent`), the node will save to the `output/` folder inside the ComfyUI server working directory (for example `output/my_latent.pt`).
- If no file extension is specified when saving, the node will append `.pt` by default.
- When loading and no extension is given, the loader will search for files with supported extensions in this order: `.pt`, `.pth`, `.latent`, `.npz`, `.npy` and pick the first match.

Examples:

- Save node: `path = my_latent` → saved to `output/my_latent.pt`
- Save node: `path = folder/sub/latent1` → saved to `output/folder/sub/latent1.pt`
- Load node: `path = my_latent` → looks for `output/my_latent.pt`, then `.pth`, etc.

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

1. Скопируйте корневую папку этого репозитория в каталог `custom_nodes` ComfyUI.
2. Перезапустите сервер ComfyUI.
3. Ноды появятся в категории `mr-asa/WAN 2.2`.

## Использование

### Сохранение

- Вход `latent` — латентное представление из модели WAN 2.2.
- Вход `path` — строка пути, например `C:/latents/my_latent.pt`.

### Загрузка

- Вход `path` — путь к файлу латента.
- Необязательный параметр `wrap_for_wan_video` — обернуть загруженный латент в dict, совместимый с WanVideoSampler.
- Выход — объект `LATENT` или dict, совместимый с WanVideoSampler, который можно передать дальше по графу.

## Структура

- `nodes.py` — реализация нод.
- `__init__.py` — экспорт маппингов нод.

## Примечания

- Директория для сохранения создаётся автоматически, если она не существует.
- `.latent` поддерживается как псевдоним для PyTorch-сериализованных латентов.
- При загрузке `.npz` используется поле `latent`, если оно есть; иначе берётся первый массив.

### Относительные пути и формат по умолчанию

- Если указан относительный путь или только имя файла (например `my_latent` или `folder/my_latent`), нод сохранит файл в папку `output/` в рабочей директории ComfyUI (например `output/my_latent.pt`).
- Если при сохранении не указано расширение, нод автоматически добавит `.pt`.
- При загрузке, если расширение не указано, загрузчик будет искать файлы с расширениями в порядке: `.pt`, `.pth`, `.latent`, `.npz`, `.npy` и загрузит первый найденный.

Примеры:

- Save node: `path = my_latent` → сохранится как `output/my_latent.pt`
- Save node: `path = folder/sub/latent1` → сохранится как `output/folder/sub/latent1.pt`
- Load node: `path = my_latent` → будет проверять `output/my_latent.pt`, затем `.pth` и т.д.
