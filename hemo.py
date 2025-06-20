import os
import random
from graphviz import Digraph

# Atur path Graphviz jika diperlukan (Windows)
os.environ["PATH"] += os.pathsep + r"C:\Users\Akram\Documents\windows_10_cmake_Release_Graphviz-13.0.1-win64\Graphviz-13.0.1-win64\bin"

# Data silsilah (bebas = status akan di-random karena tidak punya orang tua dan belum diinisialisasi)
data = """
ID,Name,Gender,FatherID,MotherID,Pasangan,InitialStatus
P1,Rina,F,,,P2,carrier
P2,Budi,M,,,P1,normal
C1,Andi,M,,,C2,normal
C2,Sari,F,P2,P1,C1,
C3,Rama,M,,,C6,normal
C4,Fitri,F,C1,C2,,
C7,Sauqi,M,C1,C2,,
C5,Sandy,M,P2,P1,,
C6,Nindy,F,P2,P1,C3,
C8,Ilham,M,C3,C6,,
C9,Dito,M,C1,C2,,
C10,Laras,F,C1,C2,,
C11,Faisal,M,C5,C12,,
C12,Ayu,F,,,C5,normal
C13,Putra,M,C5,C12,,
"""

# Parsing data
individuals = {}
for line in data.strip().split('\n')[1:]:
    parts = line.strip().split(',')
    while len(parts) < 7:
        parts.append('')
    id_, name, gender, father, mother, pasangan, status = parts
    individuals[id_] = {
        'name': name,
        'gender': gender,
        'father_id': father or None,
        'mother_id': mother or None,
        'pasangan': pasangan or None,
        'status': status or None
    }


# Mapping pasangan → anak
marriages = {}
for id_, info in individuals.items():
    pasangan = info['pasangan']
    if pasangan:
        key = tuple(sorted((id_, pasangan)))
        marriages[key] = []

for id_, info in individuals.items():
    ayah = info['father_id']
    ibu = info['mother_id']
    if ayah and ibu:
        key = tuple(sorted((ayah, ibu)))
        if key in marriages:
            marriages[key].append(id_)

# Fungsi probabilistik pewarisan hemofilia
def determine_status(mom_status, dad_status, gender):
    if gender == 'M':
        # Anak laki-laki -> X dari ibu, Y dari ayah
        if mom_status == 'carrier':
            return random.choice(['normal', 'penderita']) 
        elif mom_status == 'penderita':
            return 'penderita'
        else:
            return 'normal'
    else:
        # Anak perempuan → X dari ibu, X dari ayah
        if mom_status == 'carrier' and dad_status == 'penderita':
            return random.choice(['carrier', 'penderita']) 
        elif mom_status == 'carrier' and dad_status == 'normal':
            return random.choice(['carrier', 'normal']) 
        elif mom_status == 'penderita' and dad_status == 'normal':
            return 'carrier'
        elif mom_status == 'penderita' and dad_status == 'penderita':
            return 'penderita'
        else:
            return 'normal'

# Propagasi status (DFS)
def propagate_status(current_id):
    for child_id, child in individuals.items():
        if child['status'] is None and child['father_id'] and child['mother_id']:
            if current_id in (child['father_id'], child['mother_id']):
                dad = child['father_id']
                mom = child['mother_id']
                if individuals[dad]['status'] and individuals[mom]['status']:
                    child['status'] = determine_status(
                        individuals[mom]['status'],
                        individuals[dad]['status'],
                        child['gender']
                    )
                    propagate_status(child_id)

# Simpan status awal sebelum propagasi
initial_individuals = {k: v.copy() for k, v in individuals.items()}

# Fungsi visualisasi
def draw_graph(indiv_map, marriages, filename):
    dot = Digraph(comment=filename)
    dot.attr(rankdir='TB', splines='polyline', nodesep='1', ranksep='1.2')

    def node_style(id_, info):
        label = info['name']
        shape = 'box' if info['gender'] == 'M' else 'ellipse'
        fill = 'lightblue' if info['gender'] == 'M' else 'lightpink'
        if info['status']:
            if info['status'] == 'normal':
                label += '\n(normal)'
            elif info['status'] == 'carrier':
                label += '\n(carrier)'
            elif info['status'] == 'penderita':
                label += '\n(hemofilia)'
        return {'label': label, 'shape': shape, 'style': 'filled', 'fillcolor': fill}

    for id_, info in indiv_map.items():
        dot.node(id_, **node_style(id_, info))

    for (p1, p2), children in marriages.items():
        if children:
            marriage_id = f"marriage_{p1}_{p2}"
            dot.node(marriage_id, label="", shape="point", width="0.01")
            dot.edge(p1, marriage_id, arrowhead="none")
            dot.edge(p2, marriage_id, arrowhead="none")
            for child in children:
                dot.edge(marriage_id, child)
        else:
            with dot.subgraph() as s:
                s.attr(rank='same')
                s.edge(p1, p2, dir='none', constraint='false')

    dot.render(filename, format='png', cleanup=True)

# Gambar silsilah awal (sebelum propagasi)
draw_graph(initial_individuals, marriages, "silsilah_awal")

# Lakukan propagasi
for id_, info in individuals.items():
    if info['status']:
        propagate_status(id_)

# Gambar silsilah akhir (setelah propagasi)
draw_graph(individuals, marriages, "silsilah_akhir")
