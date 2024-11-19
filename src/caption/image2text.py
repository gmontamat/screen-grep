"""
Define image2text models
- OCR: tesseract
- BLIP: https://huggingface.co/Salesforce/blip-image-captioning-large
- Llama 3.2 Vision: https://huggingface.co/meta-llama/Llama-3.2-11B-Vision-Instruct
"""

import pytesseract
import torch
from PIL import Image
from transformers import (
    AutoModelForCausalLM,
    AutoProcessor,
    BlipForConditionalGeneration,
    BlipProcessor,
    MllamaForConditionalGeneration,
)

MODELS_DIR = "data/models"


class ScreenshotReader:

    def __init__(self, model_id: str):
        self.model_id = model_id

    def generate_caption(self, image_path: str) -> str:
        raise NotImplementedError


class TesseractOCR(ScreenshotReader):

    def __init__(self):
        super().__init__("tesseract")

    def generate_caption(self, image_path: str) -> str:
        raw_image = Image.open(image_path).convert("RGB")
        return pytesseract.image_to_string(raw_image)


class BlipCaption(ScreenshotReader):

    def __init__(self, model_id="Salesforce/blip-image-captioning-large"):
        super().__init__(model_id)
        self.processor = BlipProcessor.from_pretrained(self.model_id)
        self.model = BlipForConditionalGeneration.from_pretrained(self.model_id)

    def generate_caption(self, image_path: str) -> str:
        raw_image = Image.open(image_path).convert("RGB")
        # conditional image captioning
        text = "a screenshot of"
        inputs = self.processor(raw_image, text, return_tensors="pt")
        out = self.model.generate(**inputs)
        return self.processor.decode(out[0], skip_special_tokens=True)


class LlamaCaption(ScreenshotReader):

    def __init__(self, model_id="meta-llama/Llama-3.2-11B-Vision-Instruct"):
        super().__init__(model_id)
        # TODO: optimize for CPU
        self.model = MllamaForConditionalGeneration.from_pretrained(
            self.model_id,
            torch_dtype=torch.bfloat16,
            cache_dir=MODELS_DIR,
            # device_map="auto",
        )
        self.processor = AutoProcessor.from_pretrained(self.model_id)

    def generate_caption(self, image_path: str) -> str:
        raw_image = Image.open(image_path).convert("RGB")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": "What is this screenshot showing? Give a detailed description."},
                ],
            }
        ]
        input_text = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = self.processor(raw_image, input_text, add_special_tokens=False, return_tensors="pt").to(
            self.model.device
        )
        output = self.model.generate(**inputs, max_new_tokens=120)
        return self.processor.decode(output[0])


class FlorenceCaption(ScreenshotReader):

    def __init__(self, model_id: str = "microsoft/Florence-2-large"):
        super().__init__(model_id)
        self.device = "cpu"  # "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float32  # torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id, torch_dtype=self.torch_dtype, trust_remote_code=True,
            cache_dir=MODELS_DIR,
        ).to(self.device)
        self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)

    def generate_caption(self, image_path: str) -> str:
        prompt = "<MORE_DETAILED_CAPTION>"
        raw_image = Image.open(image_path).convert("RGB")
        inputs = self.processor(text=prompt, images=raw_image, return_tensors="pt").to(self.device, self.torch_dtype)
        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            num_beams=3,
            do_sample=False,
        )
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = self.processor.post_process_generation(
            generated_text, task=prompt, image_size=(raw_image.width, raw_image.height)
        )
        return parsed_answer[prompt]
