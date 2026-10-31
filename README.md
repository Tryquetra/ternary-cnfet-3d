# Ternary CNFET 3D Visualization (Blender 4.5)

Modelagem atômica procedural, materiais PBR e animação operacional em 3D de **Transistores de Efeito de Campo de Nanotubos de Carbono (CNFETs)** com arquitetura *Gate-All-Around* (GAA), demonstrando o transporte balístico de elétrons e a **modulação de tensão de limiar por diâmetro ($V_{th} \propto 1/d_{\text{CNT}}$)** aplicada em circuitos integrados de lógica ternária balanceada ($\{-1, 0, +1\}$).

![Estado Ternário 0: Tubo Largo (13,0) Conduzindo vs. Tubo Estreito (7,0) Bloqueado](renders/cnfet_ternary_state0.png)

---

## 1. Fundamento Físico: Limiar Multi-Valorado por Quiralidade

Nos transistores CNFET, o canal condutor é formado por nanotubos de carbono de parede única (*Single-Walled Carbon Nanotubes*, SWCNTs). Para nanotubos semicondutores do tipo zigzag $(n, 0)$, o diâmetro físico $d_{\text{CNT}}$, a banda proibida (*bandgap*, $E_g$) e a tensão de limiar ($V_{th}$) obedecem às relações:

$$d_{\text{CNT}} = \frac{\sqrt{3} a_{\text{CC}}}{\pi} n \approx 0.0783 \cdot n\text{ (nm)}$$

$$E_g \approx \frac{0.84\text{ eV}}{d_{\text{CNT}}\text{ (nm)}}, \qquad V_{th} \approx \frac{0.43\text{ V}}{d_{\text{CNT}}\text{ (nm)}}$$

Ao integrar dois nanotubos de diâmetros distintos sob um mesmo barramento de porta ($V_{GS}$), obtêm-se dois patamares de chaveamento ativos no mesmo substrato, viabilizando portas ternárias (STI, PTI, NTI e arquiteturas ternárias balanceadas como Setun / REBEL-6) sem divisores resistivos passivos:

| Parâmetro | Canal 1: SWCNT `(13,0)` (Frontal) | Canal 2: SWCNT `(7,0)` (Traseiro) |
| :--- | :---: | :---: |
| **Diâmetro Físico ($d_{\text{CNT}}$)** | $1.02\text{ nm}$ | $0.55\text{ nm}$ |
| **Tensão de Limiar ($V_{th}$)** | **$V_{th1} \approx 0.42\text{ V}$ (Baixo)** | **$V_{th2} \approx 0.78\text{ V}$ (Alto)** |
| **Malha Atômica Gerada (`bmesh`)** | 726 átomos de C ($sp^2$), 1078 ligações $\sigma$ | 518 átomos de C ($sp^2$), 770 ligações $\sigma$ |
| **Estado `-1` ($V_{GS} < 0.42\text{ V}$)** | Bloqueado ($E_{C1}$ alta) | Bloqueado ($E_{C2}$ alta) |
| **Estado `0` ($0.42\text{ V} \le V_{GS} < 0.78\text{ V}$)** | **Condução Balística ($E_{C1}$ baixa)** | **Bloqueado ($E_{C2}$ alta)** |
| **Estado `+1` ($V_{GS} \ge 0.78\text{ V}$)** | Condução Balística ($E_{C1}$ baixa) | **Condução Balística ($E_{C2}$ baixa)** |

---

## 2. Galeria de Estados Operacionais

### Progressão dos 3 Estados Ternários (`-1`, `0`, `+1` nos Quadros 20, 85 e 160)
![Progressão dos 3 Estados Ternários](renders/cnfet_ternary_3states.png)

### Anatomia de Canal Único `SWCNT (9,0)` e Transporte Balístico
![CNFET de Canal Único](renders/cnfet_single_channel_on.png)

![Comparação OFF vs ON em Canal Único](renders/cnfet_single_channel_states.png)

---

## 3. Estrutura do Repositório

* [`blend/cnfet_ternary_threshold.blend`](blend/cnfet_ternary_threshold.blend): Cena completa no Blender 4.5 LTS contendo os dois canais SWCNT `(13,0)` e `(7,0)`, contatos de Paládio/Ouro ($\text{Pd}/\text{Au}$), dielétrico high-k $\text{HfO}_2$ ($\text{IOR} = 1.90$) em corte de seção, colar metálico GAA, portadores emissivos e curvas 3D das bandas de condução $E_{C1}$ e $E_{C2}$ animadas via *Shape Keys* (quadros 1 a 180).
* [`scripts/build_ternary_cnfet.py`](scripts/build_ternary_cnfet.py): Script Python (`bpy` / `bmesh`) que reconstrói parametricamente toda a geometria atômica, materiais PBR, iluminação de estúdio em três pontos, rótulos 3D e keyframes de animação.
* [`renders/`](renders/): Capturas renderizadas em EEVEE Next em alta resolução.
* [`docs/plan.md`](docs/plan.md): Especificação arquitetural da cena e coleções.
* [`docs/walkthrough.md`](docs/walkthrough.md): Documentação detalhada da física e das camadas visuais.

---

## 4. Como Reproduzir ou Executar no Blender

Para abrir diretamente o projeto pronto:

```bash
blender blend/cnfet_ternary_threshold.blend
```

Para regerar a cena do zero via linha de comando a partir do script procedural:

```bash
blender --python scripts/build_ternary_cnfet.py
```
