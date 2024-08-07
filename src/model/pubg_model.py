from transitions import Machine


class PubgModel:

    def __init__(self) -> None:
        states = ['no_game', 'lobby', 'mathching', 'loading hall', 'plane', 'parachute', 'ground']
        self.machine = Machine(model=self, states=states, initial='no_game');
        self.machine.add_transition(trigger='start_game', source='no_game', dest='lobby', conditions=['check_lobby'])
        
        # 获取窗口大小
        pass

    def check_lobby(self) -> bool:
        return False;