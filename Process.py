from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from abc import ABC, abstractmethod
from web_automation.go_frontend import GoActions
from web_automation.go_backend import GoWeb

@dataclass
class WorkItem:
    id : int
    payload : Optional[dict] = field(default_factory=dict)
    item_status : dict = field(
        default_factory= lambda: {
            'state' : None,
            'exception_type' : None,
            'exception_message' : ''
        }
    )

class ProcessingMethod(ABC):

    def grab_input_item_data(self, item) -> Tuple[int,dict]:
        return item.id, item.payload

    @abstractmethod
    def create_payload(self) -> List[dict]:
        raise NotImplementedError

    @abstractmethod
    def process_work_item(self, item) -> Tuple[int,dict]:
        raise NotImplementedError

class DefaultProcessingMethod(ProcessingMethod):
    def create_payload(self) -> List[dict]:
        payload = []
        for i in range(1,10):
            payload.append(
                    {
                        i : i
                    }
                )
        return payload
    def process_work_item(self, item : WorkItem) -> None:
        if item.id % 2 == 0:
            raise Exception('Trigger exception on purpose.')
        return item.id, {'data':item.id}

class GoScraperBackendProcessingMethod(ProcessingMethod):
    def create_payload(self) -> List[dict]: 
        payload = []
        # grab top 50 players
        for i in range(1,51):
            payload.append(
                    {
                        'Rank' : i
                    }
                )
        return payload
    def process_work_item(self, item : WorkItem) -> Tuple[int,dict]:
        go_web = GoWeb() 
        id,input = self.grab_input_item_data(item)
        player_rank = input['Rank']
        return id, {
            'Name' : go_web.get_player_name_by_rank(player_rank),
            'Elo' : go_web.get_player_elo_by_rank(player_rank)
        }

class GoScraperFrontendProcessingMethod(ProcessingMethod):
    def create_payload(self) -> List[dict]: 
        payload = []
        # grab top 10 players 
        for i in range(1,11):
            payload.append(
                    {
                        'Rank' : i
                    }
                )
        return payload
    def process_work_item(self, item : WorkItem) -> Tuple[int,dict]:
        go_actions = GoActions() 
        id,input = self.grab_input_item_data(item)
        player_rank = input['Rank']
        try:
            go_actions.launch()
            player_name = go_actions.get_player_name(player_rank)
            player_win_rate = go_actions.get_player_win_rate(player_rank)
        except Exception as e:
            raise Exception(e)
        finally:
            go_actions.tear_down()
        return id, {
            'Name' : player_name,
            'Winrate' : player_win_rate
        }