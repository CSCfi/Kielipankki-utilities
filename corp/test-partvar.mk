# -*- coding: utf-8 -*-

# Testing functions partvar* in corp-common.mk for finding the values
# of variables specific to a corpus part (subcorpus or parallel corpus
# language)


include corp-common.mk

DEBUG = 1

PARCORP_LANG = fi
SUBCORPUS = x

# Starred values are the ones to choose
A = a *
B = b
B_other = bother
B_fi = bfi *
C = c
C_other = cother *
D = d
D_y = dy
D_x = dx
D_x_other = dxother *
D_other = dother
E = e *
E_y = ey
F = f
F_x = fx *
G = g
G_x = gx
G_x_fi = gxfi *
G_x_other = gxother
H = h *
H_y_fi = hyfi
I = i *
I_y_other = iyother
J = J
J_x = jx
J_x_other = jxother *

A := $(call partvar_or_default,A,adef)
B := $(call partvar_or_default,B,bdef)
C := $(call partvar_or_default,C,cdef)
D := $(call partvar_or_default,D,ddef)
E := $(call partvar_or_default,E,edef)
F := $(call partvar_or_default,F,fdef)
G := $(call partvar_or_default,G,gdef)
H := $(call partvar_or_default,H,hdef)
I := $(call partvar_or_default,I,idef)
J := $(call partvar_or_default,J,jdef)
K := $(call partvar_or_default,K,kdef *)

$(call showvars,A B C D E F G H I J K)

$(error End of test)
