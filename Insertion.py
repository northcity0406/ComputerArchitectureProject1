import math
class Instructions:
    def __init__(self,Data_start = 0,Data_end = 0):
        self.instruction = {
            '010000':'J',
            '010001':'JR',
            '010010':'BEQ',
            '010011':'BLTZ',
            '010100':'BGTZ',
            '010101':'BREAK',
            '010110':'SW',
            '010111':'LW',
            '011000':'SLL',
            '011001':'SRL',
            '011010':'SRA',
            '011011':'NOP',

            '110000':'ADD',
            '110001':'SUB',
            '110010':'MUL',
            '110011':'AND',
            '110100':'OR',
            '110101':'XOR',
            '110110':'NOR',
            '110111':'SLT',
            '111000':'ADDI',
            '111001':'ANDI',
            '111010':'ORI',
            '011011':'XORI', 
        }
        self.Rdata = [0]  *  32
        self.Memory_Data = []
        self.Real_code = {}
        self.Data_start = 0
        self.Data_end = 0
        self.max_R = 32

    ##计算补码
    def Complement(self,a):
        if a != "" and a[0] == '0':
            return int(a,2)
        if a != "" and a[0] == '1':
            return -(~int(a[1:],2) + 1) - 2147483648
        
    def Register_Memory(self,Qpcode,instruct):
        if Qpcode in ['ADD','SUB','MUL','AND','OR','XOR','NOR','SLT']:  ##ADD rd,rs,rt
            x = instruct[16:21]  ##rd
            y = instruct[6:11]   ##rs
            z = instruct[11:16]  ##rt
            t = ' R%d, R%d, R%d' %(int(x,2),int(y,2),int(z,2))
            s = [int(x,2),int(y,2),int(z,2)]
            return [s,t]
        elif Qpcode in ['ADDI','ANDI','ORI','XORI']:  ##ADD rd,rs,rt
            x = instruct[16:]    ##immediate value
            y = instruct[6:11]   ##rs
            z = instruct[11:16]  ##rt
            t = ' R%d, R%d, #%d' %(int(z,2),int(y,2),int(x,2))
            s = [int(z,2),int(y,2),int(x,2)]
            return [s,t]
        elif Qpcode == 'J':   ##在256M的空间内跳动
            tmp = instruct[6:] + '00'
            t = ' #%d' %(int(tmp,2))
            s = [int(tmp,2)]
            return [s,t]
        ##JR待改进，tmp = instruct[6:11]可能不正确
        ##JR跳到寄存器tmp
        elif Qpcode == 'JR':
            tmp = instruct[6:11]  
            t = ' R%d' %(int(tmp,2))
            s = [int(tmp,2)]
            return [s,t]
        elif Qpcode == 'BEQ':
            x = instruct[16:] + '00'    ##offset
            y = instruct[6:11]   ##rs
            z = instruct[11:16]  ##rt
            t = ' R%d, R%d, #%d' %(int(y,2),int(z,2),int(x,2))
            s = [int(y,2),int(z,2),int(x,2)]
            return [s,t]
        elif Qpcode  in  ['BLTZ','BGTZ']:
            x = instruct[16:] + '00'    ##offset
            y = instruct[6:11]   ##rs
            # z = instruct[11:16]  ##rt  //rt使用不到
            t = ' R%d, #%d' %(int(y,2),int(x,2))
            s = [int(y,2),int(x,2)]         
            return [s,t]       
        elif Qpcode  in  ['BREAK','NOP']:
            s = []
            t = ""          
            return [s,t] 
        elif Qpcode  in  ['LW','SW']:
            x = instruct[16:]    ##offset
            y = instruct[6:11]   ##rs
            z = instruct[11:16]  ##rt
            t = ' R%d, %d(R%d)' %(int(z,2),int(x,2),int(y,2))
            s = [int(z,2),int(x,2),int(y,2)]          
            return [s,t] 
        elif Qpcode  in  ['SLL','SRA','SRL']:
            x = instruct[21:26]  ##offset
            y = instruct[16:21]  ##rd
            z = instruct[11:16]  ##rt
            t = ' R%d, R%d, #%d' %(int(y,2),int(z,2),int(x,2)) 
            s = [int(y,2),int(z,2),int(x,2)]           
            return [s,t]




    def Translate(self):
        f = open('sample.txt', 'r')
        g = open('disassembly.txt', 'w')
        index = 256
        Flag = True
        for each in f.readlines():
            each = each.replace('\n', '')
            tmp = each[0:6]
            if Flag == True:
                tmp_instruction = self.instruction[tmp]
                if tmp_instruction == 'BREAK':
                    self.Data_start = index + 4
                    Flag = False
                tmp_Register_Memory = self.Register_Memory(self.instruction[tmp], each)
                self.Real_code[index] = [tmp_instruction, tmp_Register_Memory[0]]
                g.write("%s\t%d\t%s%s\n" % (each, index, tmp_instruction, tmp_Register_Memory[1]))
            else:
                data = self.Complement(each)
                self.Memory_Data.append(data)
                g.write("%s\t%d\t%s\n" % (each, index, data))
                self.Data_end = index
            index += 4


    def Print_Data(self, circle, PC, instruct, h):
        print(self.Data_end - self.Data_start)
        h.write('--------------------\n')
        h.write('Cycle:%d\t%d\t%s\n' % (circle, PC, instruct))
        h.write('\n')
        h.write('Registers\n')
        r = format("R%02d:" % (0))
        for i in range(self.max_R):
            r += "\t%d" % (self.Rdata[i])
            if (i + 1) % 8 == 0:
                h.write(r)
                h.write('\n')
                r = format("R%02d:" % (i + 1))
        h.write('\n')
        h.write('Data\n')
        r = format("%d:" % (self.Data_start))
        for i in range(0, (self.Data_end - self.Data_start) // 4 + 1):
            r += "\t%d" % (self.Memory_Data[i])
            if (i + 1) % 8 == 0:
                h.write(r)
                h.write('\n')
                r = format("%d:" %((i + 1)* 4 + self.Data_start))
        h.write('\n')

    def Data_Map(self):
        h = open('simulation.txt','w')        
        PC = 256
        circle = 1
        execute = self.Real_code[PC]
        while execute[0] != 'BREAK':
            if execute[0] == 'J':
                instruct = 'J #%d' %(execute[1][0])
                self.Print_Data(circle,PC,instruct,h)
                PC = execute[1][0]
            elif execute[0] == 'JR':
                register_tmp = execute[1][0]   ##找到寄存器的序号
                instruct = 'JR R%d' %(execute[1][0])
                self.Print_Data(circle,PC,instruct,h)
                PC = self.Rdata[register_tmp]  ##取出寄存器中的值，赋给PC
            elif execute[0] == 'BEQ':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                offset = execute[1][2]          ##相对于PC的偏移
                instruct = 'BEQ R%d, R%d, #%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                if self.Rdata[register_tmp1] ==   self.Rdata[register_tmp2]:
                    PC += int(offset)  + 4      
                else:
                    PC += 4
            elif execute[0] == 'BLTZ':
                register_tmp = execute[1][0]   ##找到寄存器的序号
                offset = execute[1][1]         ##相对于PC的偏移
                instruct = 'BLTZ R%d, #%d' %(execute[1][0],execute[1][1])
                self.Print_Data(circle,PC,instruct,h)
                if self.Rdata[register_tmp] < 0:
                    PC += int(offset) + 4        
                else:
                    PC += 4               
            elif execute[0] == 'BGTZ':
                register_tmp = execute[1][0]   ##找到寄存器的序号
                offset = execute[1][1]         ##相对于PC的偏移
                instruct = 'BGTZ R%d, #%d' %(execute[1][0],execute[1][1])
                self.Print_Data(circle,PC,instruct,h)
                if self.Rdata[register_tmp] > 0:
                    PC += int(offset)  + 4       
                else:
                    PC += 4                
            elif execute[0] == 'SW':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][2]   ##找到寄存器2的序号
                offset = execute[1][1]          ##相对于寄存器2的偏移
                ##将寄存器1中的数据保存到存储中（地址为寄存器2的数据+offset)
                address = (int(offset) + self.Rdata[int(register_tmp2)] - 340) // 4
                self.Memory_Data[address] = self.Rdata[int(register_tmp1)]
                instruct = 'SW R%d, %d(R%d)' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4 
            elif execute[0] == 'LW':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][2]   ##找到寄存器2的序号
                offset = execute[1][1]          ##相对于寄存器2的偏移
                ##将寄存器1中的数据保存到存储中（地址为寄存器2的数据+offset)
                self.Rdata[int(register_tmp1)] = self.Memory_Data[(int(offset) + self.Rdata[int(register_tmp2)] - 340) // 4]
                instruct = 'LW R%d, %d(R%d)' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4 
            elif execute[0] == 'SLL':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                offset = execute[1][2]          ##移动位数
                ##将寄存器1中的数据保存到存储中（地址为寄存器2的数据+offset)
                self.Rdata[int(register_tmp1)] = (self.Rdata[int(register_tmp2)] << int(offset)) & 2147483647
                instruct = 'SLL R%d, R%d, #%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'SRL':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                offset = execute[1][2]          ##移动位数
                ##将寄存器1中的数据保存到存储中（地址为寄存器2的数据+offset)
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] >> int(offset)
                instruct = 'SRL R%d, R%d, #%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'SRA':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                offset = execute[1][2]          ##移动位数
                ##将寄存器1中的数据保存到存储中（地址为寄存器2的数据+offset)
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] >> int(offset)
                instruct = 'SRA R%d, R%d, #%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'NOP':
                instruct = 'NOP'
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'ADD':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] + self.Rdata[int(register_tmp3)]
                instruct = 'ADD R%d, R%d, R%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'SUB':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] - self.Rdata[int(register_tmp3)]
                instruct = 'SUB R%d, R%d, R%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'MUL':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] * self.Rdata[int(register_tmp3)]
                instruct = 'MUL R%d, R%d, R%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'AND':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] & self.Rdata[int(register_tmp3)]
                instruct = 'AND R%d, R%d, R%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'OR':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] | self.Rdata[int(register_tmp3)]
                instruct = 'OR R%d, R%d, R%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'XOR':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] ^ self.Rdata[int(register_tmp3)]
                instruct = 'XOR R%d, R%d, R%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'NOR':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = ~(self.Rdata[int(register_tmp2)] | self.Rdata[int(register_tmp3)])
                instruct = 'NOR R%d, R%d, R%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'SLT':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = 1 if self.Rdata[int(register_tmp2)] < self.Rdata[int(register_tmp3)] else 0
                instruct = 'SLT R%d, R%d, R%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'ADDI':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] + int(register_tmp3)
                instruct = 'ADDI R%d, R%d, #%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'ANDI':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] & int(register_tmp3)
                instruct = 'ANDI R%d, R%d, #%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'ORI':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] | int(register_tmp3)
                instruct = 'ORI R%d, R%d, #%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            elif execute[0] == 'XORI':
                register_tmp1 = execute[1][0]   ##找到寄存器1的序号
                register_tmp2 = execute[1][1]   ##找到寄存器2的序号
                register_tmp3 = execute[1][2]   ##找到寄存器3的序号
                ##将寄存器2和3中的数据保存到寄存器1中
                self.Rdata[int(register_tmp1)] = self.Rdata[int(register_tmp2)] ^ int(register_tmp3)
                instruct = 'XORI R%d, R%d, #%d' %(execute[1][0],execute[1][1],execute[1][2])
                self.Print_Data(circle,PC,instruct,h)
                PC += 4
            execute = self.Real_code[PC]
            circle += 1
        instruct = 'BREAK'
        self.Print_Data(circle,PC,instruct,h)
        h.flush()
        h.close()

if __name__ == "__main__":
    instruct = Instructions()
    instruct.Translate()
    instruct.Data_Map()