# -*- coding: utf-8 -*-


"""
Module korpimport.eaf

Model (parts of) EAF files.
"""


class EafAnnotation(object):

    def __init__(self, annot_et=None):
        if annot_et is not None:
            self._import_annot_etree(annot_et)
            self.id_ = annot_et.get('ANNOTATION_ID')
            self.value = annot_et[0].text or ''
        else:
            self.id_ = self.value = None

    def _import_annot_etree(self, annot_et):
        pass


class EafRefAnnotation(EafAnnotation):

    def __init__(self, annot_et):
        super(EafRefAnnotation, self).__init__(annot_et)

    def _import_annot_etree(self, annot_et):
        self.annot_ref = annot_et.get('ANNOTATION_REF')


class EafAlignableAnnotation(EafAnnotation):

    def __init__(self, annot_et):
        super(EafAlignableAnnotation, self).__init__(annot_et)
        
    def _import_annot_etree(self, annot_et):
        self.time_slot_ref1 = annot_et.get('TIME_SLOT_REF1')
        self.time_slot_ref2 = annot_et.get('TIME_SLOT_REF2')


class EafTier(object):

    def __init__(self, tier_et):
        self._annotations = []
        self._annot_id_map = {}
        self._import_tier_etree(tier_et)

    def __iter__(self):
        for annot in self._annotations:
            yield annot

    def __len__(self):
        return len(self._annotations)

    def _import_tier_etree(self, tier_et):
        self.ling_type_ref = tier_et.get('LINGUISTIC_TYPE_REF')
        self.parent_ref = tier_et.get('PARENT_REF')
        self.participant = tier_et.get('PARTICIPANT')
        self.id_ = tier_et.get('TIER_ID')
        for ann in tier_et.iterdescendants('ALIGNABLE_ANNOTATION',
                                           'REF_ANNOTATION'):
            self._append_annotation(ann)

    def _append_annotation(self, ann_et):
        annot = self._make_annotation(ann_et)
        if annot:
            self._annotations.append(annot)
            self._annot_id_map[annot.id_] = annot

    def _make_annotation(self, ann_et):
        if ann_et.tag == 'ALIGNABLE_ANNOTATION':
            return EafAlignableAnnotation(ann_et)
        elif ann_et.tag == 'REF_ANNOTATION':
            return EafRefAnnotation(ann_et)
        else:
            return None
