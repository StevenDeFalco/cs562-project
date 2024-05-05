class PhiOperator:
    """Class to perform operations with the Phi Operator and ESQL"""
    def __init__(self, filename):
        """"""
        self.file = filename
        self.mf_struct = self.make_struct()

    def make_struct(self):
        """Makes the MF struct given raw txt in strictly defined expected format"""
        struct = {}
        lines = []
        with open(self.file, 'r') as f:
            for line in f:
                if not line:
                    continue
                lines.append(line)
        curr_idx = 0
        while curr_idx < len(lines):
            line = lines[curr_idx]
            if line.startswith("SELECT ATTRIBUTE"):
                if lines[curr_idx + 1].startswith("NUMBER OF "):
                    # TODO Error?
                    curr_idx += 1
                    continue
                s_list = lines[curr_idx + 1].replace(" ", "").strip()
                struct["S"] = s_list.split(',')
                curr_idx += 2
                continue 
            if line.startswith("NUMBER OF GROUPING"):
                if lines[curr_idx + 1].startswith("GROUPING ATTRIB"):
                    curr_idx += 1
                    continue
                struct["n"] = int(lines[curr_idx + 1])
                # TODO check if int 
                curr_idx += 2
                continue 
            if line.startswith("GROUPING ATTRIBUTES"):
                if lines[curr_idx + 1].startswith("F-VECT"):
                    curr_idx += 1
                    continue
                v_list = lines[curr_idx + 1].replace(" ", "").strip()
                struct["V"] = v_list.split(',')
                curr_idx += 2
                continue 
            if line.startswith("F-VECT"):
                if lines[curr_idx + 1].startswith("SELECT CONDITION"):
                    curr_idx += 1
                    continue
                f_list = lines[curr_idx + 1].replace(" ", "").strip()
                struct["F"] = f_list.split(',')
                curr_idx += 2
                continue 
            if line.startswith("SELECT CONDITION"):
                if lines[curr_idx + 1].startswith("HAVING"):
                    curr_idx += 1
                    struct["sigma"] = []
                    continue
                curr_idx += 1
                conditions = []
                while not lines[curr_idx].startswith("HAVING"):
                    conditions.append(lines[curr_idx].strip())
                    curr_idx += 1
                struct["sigma"] = conditions
                continue
            if line.startswith("HAVING"):
                if curr_idx + 1 == len(lines):
                    struct["G"] = ""
                    break
                struct["G"] = lines[curr_idx + 1].strip()
                break
        return struct
