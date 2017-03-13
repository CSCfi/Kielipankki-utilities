<?xml version="1.0" encoding="UTF-8"?>

<!-- Convert SUS Fieldwork XML files to VRT. -->

<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output
      method="xml"
      omit-xml-declaration="yes"
      encoding="UTF-8"
      indent="no"/>

  <xsl:template name="newline">
    <xsl:text>&#10;</xsl:text>
  </xsl:template>

  <xsl:template name="tab">
    <xsl:text>&#09;</xsl:text>
  </xsl:template>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Remove comments and processing instructions. cwb-encode
       recognizes only single-line XML comments in VRT. -->
  <xsl:template match="comment()|processing-instruction()"/>

  <xsl:template match="/text|/piece">
    <text>
      <!-- Take into account typos in attribute names -->
      <xsl:attribute name="collection">
	<xsl:value-of select="@collection|@collecion"/>
      </xsl:attribute>
      <xsl:attribute name="lang">
	<xsl:value-of select="@xml:lang"/>
      </xsl:attribute>
      <xsl:attribute name="id_orig">
	<xsl:value-of select="@id_kpv|@id_mdf|@id_myv"/>
      </xsl:attribute>
      <xsl:attribute name="locale_orig">
	<xsl:value-of select="@locale_kpv|@locale_mdf|@locale_myv"/>
      </xsl:attribute>
      <xsl:attribute name="locale">
	<xsl:value-of select="@locale|@locale_rus|@locale_myv"/>
      </xsl:attribute>
      <xsl:attribute name="recdate">
	<xsl:value-of select="@recording_time|@recordingTime"/>
      </xsl:attribute>
      <xsl:attribute name="publ_name">
	<xsl:value-of select="@name_of_publication|@name_of_Publication"/>
      </xsl:attribute>
      <xsl:attribute name="publ_place">
	<xsl:value-of select="@publication_place"/>
      </xsl:attribute>
      <xsl:attribute name="publ_year">
	<xsl:value-of select="@publication_year"/>
      </xsl:attribute>
      <xsl:attribute name="issue">
	<xsl:value-of select="@issue_number|@issue_numbrer"/>
      </xsl:attribute>
      <xsl:attribute name="pagerange">
	<xsl:value-of select="@page_range"/>
      </xsl:attribute>
      <xsl:attribute name="textnum">
	<xsl:value-of select="@text_number"/>
      </xsl:attribute>
      <xsl:attribute name="corryear">
	<xsl:value-of select="@correction_year|@correction-year"/>
      </xsl:attribute>
      <xsl:attribute name="licence">
	<xsl:value-of select="@license"/>
      </xsl:attribute>
      <xsl:apply-templates select="@type|@id_deu|@genre_deu|@comment_deu|@interviewee|@interviewer|@locale_rus|@publisher|@corrector|@status_eng|@status_fin"/>
      <xsl:call-template name="newline"/>
      <xsl:choose>
	<xsl:when test="p">
	  <xsl:apply-templates select="p"/>
	</xsl:when>
	<xsl:when test="sentence">
	  <xsl:for-each select="sentence">
	    <paragraph>
	      <xsl:call-template name="newline"/>
	      <xsl:apply-templates select="."/>
	    </paragraph>
	    <xsl:call-template name="newline"/>
	  </xsl:for-each>
	</xsl:when>
      </xsl:choose>
    </text>
    <xsl:call-template name="newline"/>
  </xsl:template>

  <xsl:template match="p">
    <paragraph>
      <xsl:call-template name="newline"/>
      <xsl:apply-templates select="sentence"/>
    </paragraph>
    <xsl:call-template name="newline"/>
  </xsl:template>

  <xsl:template match="sentence">
    <sentence>
      <xsl:attribute name="pagenum">
	<xsl:value-of select="@pgNo"/>
      </xsl:attribute>
      <xsl:attribute name="pageline">
	<xsl:value-of select="@pgLi"/>
      </xsl:attribute>
      <xsl:attribute name="type">
	<xsl:value-of select="@type"/>
      </xsl:attribute>
      <xsl:attribute name="orig">
	<xsl:value-of select="@orig_string"/>
      </xsl:attribute>
      <xsl:attribute name="transl_deu">
	<xsl:value-of select="@deu"/>
      </xsl:attribute>
      <xsl:attribute name="paranum">
	<xsl:value-of select="@paragID"/>
      </xsl:attribute>
      <xsl:attribute name="sentnum">
	<xsl:value-of select="@sent"/>
      </xsl:attribute>
      <xsl:call-template name="newline"/>
      <xsl:apply-templates select="w"/>
    </sentence>
    <xsl:call-template name="newline"/>
  </xsl:template>

  <xsl:template match="w">
    <xsl:value-of select="@word"/>
    <xsl:text>	</xsl:text>
    <xsl:value-of select="@sID"/>
    <xsl:text>	</xsl:text>
    <xsl:value-of select="@lemma"/>
    <xsl:text>	</xsl:text>
    <xsl:value-of select="@pos"/>
    <xsl:text>	</xsl:text>
    <xsl:value-of select="@msd"/>
    <xsl:text>	</xsl:text>
    <xsl:value-of select="@orig_string"/>
    <xsl:call-template name="newline"/>
  </xsl:template>

</xsl:stylesheet>
