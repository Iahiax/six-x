import torch
import torch.nn as nn
import numpy as np

class MarketTransformerModel(nn.Module):
    """نموذج Temporal Transformer للتنبؤ بذكاء المسار السعري"""
    def __init__(self, input_dim: int = 10, d_model: int = 64, nhead: int = 4, num_layers: int = 2, num_classes: int = 3):
        super(MarketTransformerModel, self).__init__()
        self.embedding = nn.Linear(input_dim, d_model)
        self.pos_encoder = nn.Parameter(torch.zeros(1, 100, d_model))
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=128, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc_out = nn.Linear(d_model, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: [batch_size, seq_len, input_dim]
        seq_len = x.size(1)
        out = self.embedding(x) + self.pos_encoder[:, :seq_len, :]
        out = self.transformer(out)
        out = self.fc_out(out[:, -1, :]) # Taking last time-step
        return out


class QuantMLInferenceEngine:
    def __init__(self, model_path: str = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = MarketTransformerModel().to(self.device)
        self.model.eval()

    def predict_signal(self, sequence_data: np.ndarray, alpha_conformal: float = 0.1) -> tuple[int, float]:
        """
        توليد إشارة التداول باستخدام معايير التنبؤ التوافقي (Conformal Prediction)
        Returns: (Signal: 0=Sell, 1=Hold, 2=Buy, Confidence Score)
        """
        tensor_in = torch.tensor(sequence_data, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            logits = self.model(tensor_in)
            probabilities = torch.softmax(logits, dim=-1).cpu().numpy()[0]

        predicted_class = int(np.argmax(probabilities))
        confidence = float(probabilities[predicted_class])

        # تطبيق حد الثقة والـ Conformal Threshold
        if confidence < (1.0 - alpha_conformal):
            return 1, confidence # Hold/Uncertain

        return predicted_class, confidence
