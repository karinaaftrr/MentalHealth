"""
Modul Evaluasi: Sistem Pakar Deteksi Kesehatan Mental pada Generasi Z
Menyediakan kalkulasi metrik evaluasi ilmiah (Akurasi, Presisi, Recall, F1-Score,
Confusion Matrix) dan visualisasi grafik menggunakan Matplotlib & scikit-learn.
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg') # Mode non-GUI untuk headless / server backend
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)
from typing import Dict, List, Any


def compute_evaluation_metrics(
    y_true: List[str],
    y_pred: List[str],
    labels: List[str]
) -> Dict[str, Any]:
    """
    Menghitung seluruh metrik evaluasi pengujian berbasis aturan.
    """
    acc = float(accuracy_score(y_true, y_pred))
    
    # Metrik agregat macro dan weighted
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average='macro', zero_division=0
    )
    p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average='weighted', zero_division=0
    )
    
    # Metrik per kelas
    p_class, r_class, f1_class, support_class = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average=None, zero_division=0
    )
    
    per_class_dict = {}
    for idx, lbl in enumerate(labels):
        per_class_dict[lbl] = {
            "precision": float(round(p_class[idx], 4)),
            "recall": float(round(r_class[idx], 4)),
            "f1_score": float(round(f1_class[idx], 4)),
            "support": int(support_class[idx])
        }
        
    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()
    
    report_text = classification_report(
        y_true, y_pred, labels=labels, zero_division=0
    )
    
    return {
        "total_samples": len(y_true),
        "accuracy": float(round(acc, 4)),
        "accuracy_percentage": float(round(acc * 100, 2)),
        "macro_avg": {
            "precision": float(round(p_macro, 4)),
            "recall": float(round(r_macro, 4)),
            "f1_score": float(round(f1_macro, 4))
        },
        "weighted_avg": {
            "precision": float(round(p_weighted, 4)),
            "recall": float(round(r_weighted, 4)),
            "f1_score": float(round(f1_weighted, 4))
        },
        "per_class": per_class_dict,
        "confusion_matrix": cm,
        "labels": labels,
        "classification_report_text": report_text
    }


def plot_confusion_matrix_figure(
    cm_data: List[List[int]],
    labels: List[str],
    display_names: List[str],
    save_path: str
) -> None:
    """
    Membuat grafik visualisasi Confusion Matrix yang rapi dan profesional.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    cm_arr = np.array(cm_data)
    
    fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)
    
    cax = ax.matshow(cm_arr, cmap=plt.cm.Blues, alpha=0.85)
    fig.colorbar(cax, shrink=0.8)
    
    # Label sumbu
    ax.set_xticks(range(len(display_names)))
    ax.set_yticks(range(len(display_names)))
    ax.set_xticklabels(display_names, rotation=35, ha='left', fontsize=9, fontweight='medium')
    ax.set_yticklabels(display_names, fontsize=9, fontweight='medium')
    
    ax.set_xlabel('Prediksi Sistem Pakar (Forward Chaining)', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_ylabel('Label Acuan (Ground Truth)', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_title('Confusion Matrix Pengujian Sistem Pakar', fontsize=12, fontweight='bold', pad=20)
    
    # Isi angka dalam setiap sel matriks
    threshold = cm_arr.max() / 2.0 if cm_arr.max() > 0 else 1.0
    for i in range(cm_arr.shape[0]):
        for j in range(cm_arr.shape[1]):
            val = cm_arr[i, j]
            color = 'white' if val > threshold else '#0F172A'
            ax.text(j, i, str(val), ha='center', va='center', color=color, fontsize=11, fontweight='bold')
            
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)


def plot_accuracy_bar_chart(accuracy: float, total_samples: int, save_path: str) -> None:
    """
    Membuat visualisasi grafik akurasi keseluruhan sistem.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    
    acc_pct = accuracy * 100.0
    bars = ax.bar(['Akurasi Sistem'], [acc_pct], color='#2563EB', width=0.4, edgecolor='#1D4ED8', linewidth=1.5)
    
    ax.set_ylim(0, 110)
    ax.set_ylabel('Tingkat Kesesuaian (%)', fontsize=11, fontweight='bold')
    ax.set_title(f'Tingkat Akurasi Pengujian (N = {total_samples} Kasus)', fontsize=12, fontweight='bold', pad=15)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Label nilai di atas bar
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 6),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold', color='#1E3A8A')
                    
    # Keterangan ilmiah di bawah
    plt.figtext(0.5, 0.01,
                "Catatan: Metrik mengukur konsistensi penalaran deduktif aturan Forward Chaining terhadap kasus uji acuan.",
                ha='center', fontsize=8, color='#64748B')
                
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)


def plot_precision_recall_f1_chart(
    per_class_metrics: Dict[str, Dict[str, float]],
    display_names: Dict[str, str],
    save_path: str
) -> None:
    """
    Membuat diagram batang metrik per kelas (Precision, Recall, F1-Score).
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    labels = list(per_class_metrics.keys())
    x = np.arange(len(labels))
    width = 0.25
    
    precisions = [per_class_metrics[l]["precision"] * 100 for l in labels]
    recalls = [per_class_metrics[l]["recall"] * 100 for l in labels]
    f1s = [per_class_metrics[l]["f1_score"] * 100 for l in labels]
    names = [display_names.get(l, l) for l in labels]
    
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    
    rects1 = ax.bar(x - width, precisions, width, label='Precision', color='#3B82F6', edgecolor='#1D4ED8')
    rects2 = ax.bar(x, recalls, width, label='Recall', color='#10B981', edgecolor='#047857')
    rects3 = ax.bar(x + width, f1s, width, label='F1-Score', color='#F59E0B', edgecolor='#B45309')
    
    ax.set_ylabel('Nilai (%)', fontsize=11, fontweight='bold')
    ax.set_title('Perbandingan Precision, Recall, dan F1-Score per Kondisi', fontsize=12, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=25, ha='right', fontsize=9, fontweight='medium')
    ax.set_ylim(0, 115)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)


def plot_comprehensive_evaluation_chart(
    metrics: Dict[str, Any],
    display_names: Dict[str, str],
    save_path: str
) -> None:
    """
    Membuat grafik komposit ringkasan evaluasi (Accuracy, Macro-Avg, Weighted-Avg).
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=300)
    
    # Panel 1: Perbandingan Agregat
    agg_names = ['Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1', 'Weighted F1']
    agg_values = [
        metrics['accuracy'] * 100,
        metrics['macro_avg']['precision'] * 100,
        metrics['macro_avg']['recall'] * 100,
        metrics['macro_avg']['f1_score'] * 100,
        metrics['weighted_avg']['f1_score'] * 100
    ]
    colors = ['#2563EB', '#0D9488', '#10B981', '#F59E0B', '#8B5CF6']
    
    bars1 = ax1.bar(agg_names, agg_values, color=colors, width=0.55, edgecolor='#334155', linewidth=1)
    ax1.set_ylim(0, 115)
    ax1.set_ylabel('Persentase (%)', fontsize=10, fontweight='bold')
    ax1.set_title('Metrik Agregat Sistem Pakar', fontsize=11, fontweight='bold', pad=12)
    ax1.set_xticks(range(len(agg_names)))
    ax1.set_xticklabels(agg_names, rotation=30, ha='right', fontsize=8.5)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)
    
    for bar in bars1:
        h = bar.get_height()
        ax1.annotate(f'{h:.1f}%',
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4),
                     textcoords="offset points",
                     ha='center', va='bottom', fontsize=9, fontweight='bold')
                     
    # Panel 2: Distribusi Support Sampel
    labels = metrics['labels']
    supports = [metrics['per_class'][l]['support'] for l in labels]
    lbl_names = [display_names.get(l, l) for l in labels]
    
    bars2 = ax2.barh(lbl_names, supports, color='#64748B', height=0.5, edgecolor='#334155')
    ax2.set_xlabel('Jumlah Kasus Uji (Kasus)', fontsize=10, fontweight='bold')
    ax2.set_title(f'Distribusi Kasus Acuan (Total: {metrics["total_samples"]})', fontsize=11, fontweight='bold', pad=12)
    ax2.grid(axis='x', linestyle='--', alpha=0.4)
    
    for bar in bars2:
        w = bar.get_width()
        ax2.annotate(f'{int(w)}',
                     xy=(w, bar.get_y() + bar.get_height() / 2),
                     xytext=(5, 0),
                     textcoords="offset points",
                     ha='left', va='center', fontsize=9, fontweight='bold')
                     
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)
