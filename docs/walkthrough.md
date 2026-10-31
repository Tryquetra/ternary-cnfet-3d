# Walkthrough: Comparação de Limiar Ternário em CNFETs no Blender 4.5

A cena no arquivo [`blend/cnfet_ternary_threshold.blend`](../blend/cnfet_ternary_threshold.blend) implementa uma arquitetura de **duplo canal paralelo** compartilhando Fonte, Dreno e barramento de Porta ($V_{GS}$) para demonstrar fisicamente a modulação de tensão de limiar em lógica ternária balanceada ($\{-1, 0, +1\}$).

---

## 1. Visualização Renderizada dos Estados Ternários

### A. Estado Ternário `0` (Quadro 85: Condução Seletiva por Diâmetro)
![Estado Ternário 0 (Quadro 85): Tubo Largo (13,0) em Condução Balística e Tubo Estreito (7,0) Bloqueado](../renders/cnfet_ternary_state0.png)

### B. Progressão Completa dos 3 Estados Ternários (`-1`, `0`, `+1`)
![Progressão dos 3 Estados Ternários: Estado -1 (Quadro 20), Estado 0 (Quadro 85) e Estado +1 (Quadro 160)](../renders/cnfet_ternary_3states.png)

### C. Modelo de Canal Único `SWCNT (9,0)`
![Visão Geral do CNFET Gate-All-Around de Canal Único no Estado ON](../renders/cnfet_single_channel_on.png)

![Sequência de Operação de Canal Único: Estado OFF vs. Condução Balística ON](../renders/cnfet_single_channel_states.png)

---

## 2. Física da Modulação de Limiar por Diâmetro ($V_{th} \propto 1 / d_{\text{CNT}}$)

O diâmetro de um nanotubo zigzag $(n, 0)$ é dado por:

$$d_{\text{CNT}} = \frac{\sqrt{3} a_{\text{CC}}}{\pi} n \approx 0.0783 \cdot n\text{ (nm)}$$

A banda proibida $E_g$ e a tensão de limiar $V_{th}$ são inversamente proporcionais ao diâmetro físico do nanotubo:

$$E_g \approx \frac{0.84\text{ eV}}{d_{\text{CNT}}\text{ (nm)}}, \qquad V_{th} \approx \frac{0.43\text{ V}}{d_{\text{CNT}}\text{ (nm)}}$$

| Parâmetro Físico e Geométrico | Canal 1 Frontal: Tubo Largo `(13,0)` | Canal 2 Traseiro: Tubo Estreito `(7,0)` |
| :--- | :---: | :---: |
| **Diâmetro Físico ($d_{\text{CNT}}$)** | $1.02\text{ nm}$ | $0.55\text{ nm}$ |
| **Tensão de Limiar ($V_{th}$)** | **$V_{th1} \approx 0.42\text{ V}$ (Baixo)** | **$V_{th2} \approx 0.78\text{ V}$ (Alto)** |
| **Geometria Atômica no Blender** | 726 átomos de C, 1078 ligações $\sigma$ ($R = 0.56$) | 518 átomos de C, 770 ligações $\sigma$ ($R = 0.32$) |
| **Curva da Banda de Condução** | `Ec1_LowVth_Wide` (Ciano frontal) | `Ec2_HighVth_Narrow` (Rosa/Âmbar) |
| **Estado `-1` ($V_{GS} < 0.42\text{ V}$, Quadros 1 a 45)** | Bloqueado ($E_{C1}$ alta) | Bloqueado ($E_{C2}$ alta) |
| **Estado `0` ($0.42\text{ V} \le V_{GS} < 0.78\text{ V}$, Quadros 65 a 115)** | **Conduzindo ($E_{C1}$ baixa)** | **Bloqueado ($E_{C2}$ alta)** |
| **Estado `+1` ($V_{GS} \ge 0.78\text{ V}$, Quadros 135 a 180)** | Conduzindo ($E_{C1}$ baixa) | **Conduzindo ($E_{C2}$ baixa)** |
