/**
 * SCRIPT.JS: Sistem Pakar Deteksi Kesehatan Mental Generasi Z
 * Validasi form kuesioner, pelacakan progres pengisian interaktif,
 * dan fitur auto-fill pengujian 10 data kasus acuan (benchmark).
 */

function initQuestionnaireValidation() {
    const form = document.getElementById('screening-form');
    if (!form) return;

    const totalQuestions = 25;
    const progressText = document.getElementById('progress-text');
    const progressFill = document.getElementById('progress-fill');
    const submitBtn = document.getElementById('btn-submit');
    const validationSummary = document.getElementById('validation-summary');

    // Kumpulan kode pertanyaan K01 - K25
    const questionCodes = [];
    for (let i = 1; i <= totalQuestions; i++) {
        questionCodes.push(`K${String(i).padStart(2, '0')}`);
    }

    function updateProgress() {
        let answeredCount = 0;
        
        questionCodes.forEach(code => {
            const radios = document.getElementsByName(code);
            let isAnswered = false;
            let selectedVal = null;

            for (let r of radios) {
                const label = r.closest('.option-label');
                if (r.checked) {
                    isAnswered = true;
                    selectedVal = r.value;
                    if (label) label.classList.add('selected');
                } else {
                    if (label) label.classList.remove('selected');
                }
            }

            const card = document.getElementById(`card-${code}`);
            const statusBadge = document.getElementById(`status-${code}`);

            if (isAnswered) {
                answeredCount++;
                if (card) {
                    card.classList.add('answered');
                    card.classList.remove('has-error');
                }
                if (statusBadge) {
                    statusBadge.textContent = selectedVal === '1' ? 'Jawaban: Ya' : 'Jawaban: Tidak';
                    statusBadge.classList.add('done');
                }
            } else {
                if (card) card.classList.remove('answered');
                if (statusBadge) {
                    statusBadge.textContent = 'Belum dijawab';
                    statusBadge.classList.remove('done');
                }
            }
        });

        const percentage = Math.round((answeredCount / totalQuestions) * 100);
        if (progressText) {
            progressText.textContent = `${answeredCount} dari ${totalQuestions} terjawab (${percentage}%)`;
        }
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }

        if (validationSummary) {
            if (answeredCount === totalQuestions) {
                validationSummary.textContent = "Seluruh 25 pertanyaan telah terjawab lengkap. Siap diproses.";
                validationSummary.style.color = "#166534";
            } else {
                validationSummary.textContent = `Masih tersisa ${totalQuestions - answeredCount} pertanyaan yang belum dijawab.`;
                validationSummary.style.color = "#64748B";
            }
        }

        return answeredCount;
    }

    // Expose updateProgress agar dapat dipanggil dari luar (auto-fill)
    window.refreshQuestionnaireProgress = updateProgress;

    // Pasang listener pada seluruh radio input
    const allRadios = form.querySelectorAll('.option-radio');
    allRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateProgress();
        });
    });

    // Inisialisasi awal saat load
    updateProgress();

    // Validasi saat submit formulir
    form.addEventListener('submit', function(e) {
        const answeredCount = updateProgress();
        
        if (answeredCount < totalQuestions) {
            e.preventDefault();
            
            // Cari kartu pertama yang belum dijawab
            let firstUnansweredCard = null;
            questionCodes.forEach(code => {
                const radios = document.getElementsByName(code);
                let isChecked = false;
                for (let r of radios) {
                    if (r.checked) {
                        isChecked = true;
                        break;
                    }
                }
                const card = document.getElementById(`card-${code}`);
                if (!isChecked && card) {
                    card.classList.add('has-error');
                    if (!firstUnansweredCard) {
                        firstUnansweredCard = card;
                    }
                }
            });

            if (validationSummary) {
                validationSummary.textContent = `Mohon lengkapi seluruh ${totalQuestions} pertanyaan sebelum memproses hasil.`;
                validationSummary.style.color = "#B91C1C";
            }

            if (firstUnansweredCard) {
                firstUnansweredCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }

            alert(`Harap lengkapi seluruh 25 pertanyaan kuesioner. Terdapat ${totalQuestions - answeredCount} pertanyaan yang belum Anda jawab.`);
            return false;
        }

        // Jika valid, ubah status tombol
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Memproses Inferensi Sistem Pakar...';
        }
        return true;
    });
}

/**
 * Fitur Auto-Fill Pengujian 10 Data Kasus Acuan
 */
function initBenchmarkAutoFill() {
    const dataElement = document.getElementById('benchmark-cases-data');
    const selector = document.getElementById('benchmark-selector');
    const loadBtn = document.getElementById('btn-load-benchmark');
    const clearBtn = document.getElementById('btn-clear-answers');

    if (!dataElement || !selector) return;

    let cases = [];
    try {
        cases = JSON.parse(dataElement.textContent);
    } catch (e) {
        console.error("Gagal membaca data kasus acuan:", e);
        return;
    }

    const casesMap = {};
    cases.forEach(c => {
        casesMap[c.id_kasus] = c;
    });

    function applyCaseAnswers(caseId) {
        const selectedCase = casesMap[caseId];
        if (!selectedCase || !selectedCase.answers) return;

        for (let i = 1; i <= 25; i++) {
            const code = `K${String(i).padStart(2, '0')}`;
            const val = selectedCase.answers[code] || 0;
            const targetRadio = document.querySelector(`input[name="${code}"][value="${val}"]`);
            if (targetRadio) {
                targetRadio.checked = true;
            }
        }

        if (window.refreshQuestionnaireProgress) {
            window.refreshQuestionnaireProgress();
        }
    }

    if (loadBtn) {
        loadBtn.addEventListener('click', function() {
            const caseId = selector.value;
            if (!caseId) {
                alert("Silakan pilih salah satu kasus acuan dari dropdown terlebih dahulu.");
                return;
            }
            applyCaseAnswers(caseId);
        });
    }

    if (selector) {
        selector.addEventListener('change', function() {
            const caseId = selector.value;
            if (caseId) {
                applyCaseAnswers(caseId);
            }
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            for (let i = 1; i <= 25; i++) {
                const code = `K${String(i).padStart(2, '0')}`;
                const radios = document.getElementsByName(code);
                radios.forEach(r => r.checked = false);
            }
            if (selector) selector.value = "";
            if (window.refreshQuestionnaireProgress) {
                window.refreshQuestionnaireProgress();
            }
        });
    }

    // Jika ada kasus yang sudah terpilih saat page load (dari parameter query string)
    if (selector.value) {
        applyCaseAnswers(selector.value);
    }
}
