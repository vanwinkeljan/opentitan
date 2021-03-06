# Copyright lowRISC contributors.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import random
from typing import Optional, Tuple

from shared.insn_yaml import InsnsFile
from shared.operand import ImmOperandType, RegOperandType

from ..program import ProgInsn, Program
from ..model import Model
from ..snippet import Snippet
from ..snippet_gen import SnippetGen


class Jump(SnippetGen):
    '''A generator that makes a snippet with a JAL or JALR jump'''
    def __init__(self, insns_file: InsnsFile) -> None:
        jal = self._get_named_insn(insns_file, 'jal')
        jalr = self._get_named_insn(insns_file, 'jalr')

        # jal expects the operands: grd, offset.
        exp_shape = (len(jal.operands) == 2 and
                     isinstance(jal.operands[0].op_type, RegOperandType) and
                     jal.operands[0].op_type.reg_type == 'gpr' and
                     jal.operands[0].op_type.is_dest() and
                     isinstance(jal.operands[1].op_type, ImmOperandType) and
                     jal.operands[1].op_type.signed)
        if not exp_shape:
            raise RuntimeError('JAL instruction from instructions file is not '
                               'the shape expected by the Jump generator.')

        # jalr expects the operands: grd, grs1, offset
        exp_shape = (len(jalr.operands) == 3 and
                     isinstance(jalr.operands[0].op_type, RegOperandType) and
                     jalr.operands[0].op_type.reg_type == 'gpr' and
                     jalr.operands[0].op_type.is_dest() and
                     isinstance(jalr.operands[1].op_type, RegOperandType) and
                     jalr.operands[1].op_type.reg_type == 'gpr' and
                     not jalr.operands[1].op_type.is_dest() and
                     isinstance(jalr.operands[2].op_type, ImmOperandType) and
                     jalr.operands[2].op_type.signed)
        if not exp_shape:
            raise RuntimeError('JALR instruction from instructions file is '
                               'not the shape expected by the Jump generator.')

        self.jal = jal
        self.jalr = jalr

    def gen(self,
            size: int,
            model: Model,
            program: Program) -> Optional[Tuple[Snippet, bool, int]]:

        # Decide whether to generate JALR or JAL. In the future, we'll load
        # this weighting from somewhere else.
        jalr_weight = 1.0
        jal_weight = 1.0
        sum_weights = jalr_weight + jal_weight

        # If we try to generate a JALR and fail, try to generate a JAL instead:
        # in practice that might well work and if we return None from here, the
        # wrapper will disable us entirely this time around.
        is_jalr = random.random() < jalr_weight / sum_weights
        if is_jalr:
            ret = self.gen_jalr(size, model, program)
            if ret is not None:
                return ret

        return self.gen_jal(size, model, program)

    def _pick_jump(self,
                   base_addr: int,
                   imm_optype: ImmOperandType,
                   model: Model,
                   program: Program) -> Optional[Tuple[int, int, int]]:
        '''Pick target and link register for a jump instruction

        base_addr is the starting address (either the current PC for a JAL or
        the value of a register for a JALR). imm_optype is the OperandType for
        the immediate operand that we are generating.

        Returns (tgt, enc_offset, link_idx) where tgt is the target address,
        enc_offset is the offset (encoded as 2's complement if necessary for
        the immediate operand) and link_idx is the index of the chosen link
        register.

        '''
        # Calculate the range of addresses we can hit, starting at base_addr.
        #
        # We can assume that get_range() returns something, because it only
        # returns None if the operand has no width: not possible because we
        # know we have an encoding for the instruction.
        tgt_rng = imm_optype.get_op_val_range(base_addr)
        assert tgt_rng is not None
        tgt_min, tgt_max = tgt_rng

        # Pick a branch target. "1" here is the minimum number of instructions
        # that must fit. One is enough (we'll just end up generating another
        # branch immediately)
        tgt = program.pick_branch_target(1, tgt_min, tgt_max)
        if tgt is None:
            return None

        assert tgt_min <= tgt <= tgt_max
        enc_offset = imm_optype.op_val_to_enc_val(tgt, base_addr)
        assert enc_offset is not None

        # Pick a link register, not preferring any in particular. This should
        # never fail (it's a destination, not a source).
        link_reg_idx = model.pick_operand_value(self.jal.operands[0].op_type)
        assert link_reg_idx is not None

        return (tgt, enc_offset, link_reg_idx)

    def _add_snippet(self,
                     prog_insn: ProgInsn,
                     link_reg_idx: int,
                     new_pc: int,
                     size: int,
                     model: Model,
                     program: Program) -> Tuple[Snippet, bool, int]:
        '''Generate a 1-instruction snippet for prog_insn; finish generation'''
        # Generate our one-instruction snippet and add it to the program
        snippet = Snippet([(model.pc, [prog_insn])])
        snippet.insert_into_program(program)

        # Update the model with the instruction
        model.update_for_insn(prog_insn)

        # The model will have spotted that the link register got *some* value,
        # but it doesn't know enough about jumps to know what value that is. So
        # set that explicitly here.
        link_reg_optype = prog_insn.insn.operands[0].op_type
        assert isinstance(link_reg_optype, RegOperandType)
        model.write_reg(link_reg_optype.reg_type, link_reg_idx, model.pc + 4)

        # And update the PC, which is now tgt
        model.pc = new_pc

        return (snippet, False, size - 1)

    def gen_jal(self,
                size: int,
                model: Model,
                program: Program) -> Optional[Tuple[Snippet, bool, int]]:
        '''Generate a random JAL instruction'''
        assert len(self.jal.operands) == 2
        offset_optype = self.jal.operands[1].op_type
        assert isinstance(offset_optype, ImmOperandType)

        jmp_data = self._pick_jump(model.pc, offset_optype, model, program)
        if jmp_data is None:
            return None

        tgt, enc_offset, link_reg_idx = jmp_data

        prog_insn = ProgInsn(self.jal, [link_reg_idx, enc_offset], None)
        return self._add_snippet(prog_insn, link_reg_idx, tgt,
                                 size, model, program)

    def gen_jalr(self,
                 size: int,
                 model: Model,
                 program: Program) -> Optional[Tuple[Snippet, bool, int]]:
        '''Generate a random JALR instruction'''

        assert len(self.jalr.operands) == 3
        offset_optype = self.jalr.operands[2].op_type
        assert isinstance(offset_optype, ImmOperandType)

        # Pick a register to use as a base pointer. This needs to be something
        # where we actually know the value (rather than just knowing that it
        # has an architectural value). Note that there will always be at least
        # one such register (x0).
        known_regs = model.regs_with_known_vals('gpr')
        assert known_regs

        base_reg_idx, base_reg_val = random.choice(known_regs)

        jmp_data = self._pick_jump(base_reg_val, offset_optype, model, program)
        if jmp_data is None:
            return None

        tgt, enc_offset, link_reg_idx = jmp_data

        prog_insn = ProgInsn(self.jalr,
                             [link_reg_idx, base_reg_idx, enc_offset],
                             None)
        return self._add_snippet(prog_insn, link_reg_idx, tgt,
                                 size, model, program)
