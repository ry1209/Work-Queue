import requests
from dataclasses import dataclass
from bs4 import BeautifulSoup
from Config import config

@dataclass
class GoWeb:

    go_base_url : str = config['GO']['go_rating_webpage']

    def __post_init__(self):
        self.players_table = []
        html_table = requests.get(self.go_base_url).text
        soup = BeautifulSoup(html_table, "html.parser")
        for table_row in soup.select('tr'):
            cells = table_row.find_all('td')
            if len(cells) > 0:
                cell_values = []
                for cell in cells:
                    cell_values.append(cell.text.strip())
                if len(cell_values)>1:
                    self.players_table.append(cell_values)

    def get_player_name_by_rank(self, rank : int) -> str:
        return self.players_table[rank-1][1]
    
    def get_player_elo_by_rank(self, rank : int) -> str:
        return self.players_table[rank-1][-1]
